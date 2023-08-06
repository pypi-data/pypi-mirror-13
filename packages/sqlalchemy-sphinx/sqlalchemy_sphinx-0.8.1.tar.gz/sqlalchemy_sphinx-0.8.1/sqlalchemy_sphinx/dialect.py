""" Dialect implementaiton for SphinxQL based on MySQLdb-Python protocol"""

from sqlalchemy.engine import default
from sqlalchemy.sql import compiler
from sqlalchemy.sql.elements import ClauseList
from sqlalchemy.sql import expression as sql
from sqlalchemy.sql.functions import Function

from sqlalchemy.types import MatchType
from sqlalchemy import util

__all__ = ("SphinxDialect")


class SphinxCompiler(compiler.SQLCompiler):

    def visit_options_func(self, fn, *args, **_kw):
        """
        OPTION clause. This is a Sphinx specific extension that lets you control a number of per-query options.

        The syntax is:
        OPTION <optionname>=<value> [ , ... ]
        Supported options and respectively allowed values are:
        'ranker' - any of 'proximity_bm25', 'bm25', 'none', 'wordcount', 'proximity', 'matchany', or 'fieldmask'
        'max_matches' - integer (per-query max matches value)
        'cutoff' - integer (max found matches threshold)
        'max_query_time' - integer (max search time threshold, msec)
        'retry_count' - integer (distributed retries count)
        'retry_delay' - integer (distributed retry delay, msec)
        'field_weights' - a named integer list (per-field user weights for ranking)
        'index_weights' - a named integer list (per-index user weights for ranking)

        Example:
        SELECT * FROM test WHERE MATCH('@title hello @body world')
        OPTION ranker=bm25, max_matches=3000, field_weights=(title=10, body=3)
        """
        options_list = []
        for clause in fn.clauses.clauses:
            if clause.left.name in ["field_weights", "index_weights"]:
                option = "{}=({})"
                option = option.format(clause.left.name, ", ".join(clause.right.value))
                options_list.append(option)
            else:
                option = "{}={}"
                option = option.format(clause.left.name, clause.right.value)
                options_list.append(option)
        self.options_list = options_list
        # return "OPTION {}".format(", ".join(options_list))

    def limit_clause(self, select, **kw):
        text = ""
        if select._limit is not None and select._offset is None:
            text += "\n LIMIT 0, {}".format(select._limit)
        else:
            text += "\n LIMIT %s, %s" % (
                self.process(sql.literal(select._offset)),
                self.process(sql.literal(select._limit)))
        return text

    def visit_column(self, column, result_map=None, include_table=True, **kwargs):
        name = column.name
        is_literal = column.is_literal
        if is_literal:
            name = self.escape_literal_column(name)
        else:
            name = self.preparer.quote(name)
        return name

    def visit_match_op_binary(self, binary, operator, **kw):
        if self.left_match and self.right_match:
            match_terms = []
            for left, right in zip(self.left_match, self.right_match):
                t = "(@{} {})".format(self.process(left), right.value)
                match_terms.append(t)
            self.left_match = tuple()
            self.right_match = tuple()
            return "MATCH('{}')".format(" ".join(match_terms))

    def visit_match_func(self, fn, **kw):
        '''
        Overwrite the top level match func since Sphinx does match differently
        '''
        if self.left_match and self.right_match:
            match_terms = []
            for left, right in zip(self.left_match, self.right_match):
                t = "(@{} {})".format(self.process(left), right.value)
                match_terms.append(t)
            self.left_match = tuple()
            self.right_match = tuple()
            return "MATCH('{}')".format(" ".join(match_terms))

    def visit_distinct_func(self, func, **kw):
        return "DISTINCT {}".format(self.process(func.clauses.clauses[0]))

    def visit_select(self, select,
                     asfrom=False, parens=True, iswrapper=False,
                     fromhints=None, compound_index=1, force_result_map=False,
                     nested_join_translation=False, **kwargs):
        entry = self.stack and self.stack[-1] or {}

        existingfroms = entry.get('from', None)

        froms = select._get_display_froms(existingfroms)

        correlate_froms = set(sql._from_objects(*froms))

        # TODO: might want to propagate existing froms for
        # select(select(select)) where innermost select should correlate
        # to outermost if existingfroms: correlate_froms =
        # correlate_froms.union(existingfroms)

        self.stack.append({'from': correlate_froms,
                           'iswrapper': iswrapper})

        # the actual list of columns to print in the SELECT column list.

        unique_co = []
        distinct_alias = None
        for co in util.unique_list(select.inner_columns):
            sql_util = self._label_select_column(select, co, True, asfrom, {})
            if "DISTINCT" in sql_util:
                distinct_alias = sql_util.split(" AS ")[-1]
            unique_co.append(sql_util)
        result_columns = []
        if distinct_alias:
            for idx, rc_tuple in enumerate(self._result_columns):
                if rc_tuple[0] == distinct_alias:
                    if rc_tuple[-2][-1] == distinct_alias:
                        target_name = "@distinct"
                        temp_rc = list(rc_tuple)
                        temp_rc[0] = target_name
                        inner_tuple = list(temp_rc[-2])
                        inner_tuple[-1] = target_name
                        if not select._group_by_clause.clauses:
                            raise AssertionError("Can't query distinct if no group by  is selected")
                        temp_rc[-2] = tuple(inner_tuple)
                        result_columns.append(tuple(temp_rc))
                else:
                    result_columns.append(rc_tuple)
        if result_columns:
            self._result_columns = result_columns

        inner_columns = [
            c for c in unique_co
            if c is not None
        ]

        text = "SELECT "  # we're off to a good start !
        text += self.get_select_precolumns(select)
        text += ', '.join(inner_columns)

        text += " \nFROM "

        text += ', '.join([f._compiler_dispatch(self,
                                                asfrom=True, **kwargs)
                           for f in froms])

        def check_match_clause(clause):
            left_tuple = []
            right_tuple = []
            match_operators = []
            if isinstance(clause.type, MatchType):
                left_tuple.append(clause.left)
                right_tuple.append(clause.right)
                match_operators.append(clause.operator)
            elif isinstance(clause, Function):
                if clause.name.lower() == "match":
                    func_left, func_right = clause.clauses
                    left_tuple.append(func_left)
                    right_tuple.append(func_right)
            elif isinstance(clause, ClauseList):
                for xclause in clause.clauses:
                    l, r, m = check_match_clause(xclause)
                    left_tuple.extend(l)
                    right_tuple.extend(r)
                    match_operators.extend(m)
            return left_tuple, right_tuple, match_operators

        if select._whereclause is not None:
            # Match Clauses must be done in the same compiler
            left_tuple = []
            right_tuple = []
            match_operators = []
            l, r, m = check_match_clause(select._whereclause)
            left_tuple.extend(l)
            right_tuple.extend(r)
            match_operators.extend(m)

            if left_tuple and right_tuple:
                self.left_match = tuple(left_tuple)
                self.right_match = tuple(right_tuple)
                self.match_operators = tuple(match_operators)

            t = select._whereclause._compiler_dispatch(self, **kwargs)
            if t:
                text += " \nWHERE " + t

            if hasattr(self, "options_list"):
                if self.options_list:
                    option_text = " OPTION {}".format(", ".join(self.options_list))
                    text += option_text

        if select._group_by_clause.clauses:
            group_by = select._group_by_clause._compiler_dispatch(
                self, **kwargs)
            text += " GROUP BY " + group_by

        if select._order_by_clause.clauses:
            text += self.order_by_clause(select, **kwargs)
        if select._limit is not None:
            text += self.limit_clause(select)

        self.stack.pop(-1)
        return text


class SphinxDialect(default.DefaultDialect):

    name = "sphinx"
    statement_compiler = SphinxCompiler

    # TODO HACK : Prevent SQLalchemy to send the request
    # 'SELECT 'X' as some_label;' as it is not supported by Sphinx
    description_encoding = None

    def _check_unicode_returns(self, connection):
        return True

    def do_rollback(self, connection):
        pass

    def do_commit(self, connection):
        pass

    def do_begin(self, connection):
        pass
