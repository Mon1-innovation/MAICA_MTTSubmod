class migration_instance(object):

    def __init__(self, last_ver, curr_ver, force_current=False):
        self.last_ver, self.curr_ver = last_ver, curr_ver
        self.force_current = force_current
        self.migration_queue = []

    @staticmethod
    def _compare_versions(v1, v2):
        """Compare dotted numeric versions using the legacy 0/1/2 states."""
        try:
            first = [int(part.strip()) for part in str(v1).strip().split('.')]
            second = [int(part.strip()) for part in str(v2).strip().split('.')]
        except (TypeError, ValueError):
            return None

        if not first or not second or any(part < 0 for part in first + second):
            return None

        width = max(len(first), len(second))
        first.extend([0] * (width - len(first)))
        second.extend([0] * (width - len(second)))
        if first == second:
            return 0
        return 1 if first > second else 2

    def migrate(self):
        # Invalid schemas use None internally and retain the old public error
        # message for callers that display or compare migration results.
        signal = self._compare_versions(self.last_ver, self.curr_ver)
        if self.force_current:
            # Development builds intentionally rerun only the current entry.
            # Do not let a malformed legacy version prevent that repair path;
            # the current version still must be a valid schema.
            if self._compare_versions(self.curr_ver, self.curr_ver) is None:
                return False, 'Version schemas incompatable'
            try:
                for version, migration in self.migration_queue:
                    current_compare = self._compare_versions(version, self.curr_ver)
                    if current_compare is None:
                        return False, 'Version schemas incompatable'
                    if current_compare == 0:
                        migration()
            except Exception as error:
                return False, 'Migration failed: {}'.format(error)
            return True, 'Migration complete'

        if signal is None:
            return False, 'Version schemas incompatable'
        if signal == 0:
            return True, 'Version unchanged'
        if signal == 1:
            return False, 'Trying to revert version, denying'

        if signal == 2:
            try:
                for version, migration in self.migration_queue:
                    pending_compare = self._compare_versions(version, self.last_ver)
                    current_compare = self._compare_versions(version, self.curr_ver)
                    if pending_compare is None or current_compare is None:
                        return False, 'Version schemas incompatable'

                    is_pending = (
                        signal == 2
                        and pending_compare == 1
                        and current_compare in (2, 0)
                    )
                    if is_pending:
                        migration()
            except Exception as error:
                return False, 'Migration failed: {}'.format(error)
            return True, 'Migration complete'

        return False, 'Version schemas incompatable'
