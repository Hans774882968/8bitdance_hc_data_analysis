def sort_by_value(a):
    return sorted(a, reverse=True, key=lambda x: x[1])


def remove_zero_val(a):
    for index, val in enumerate(a):
        if not val[1]:
            return a[:index]
    return a


def make_autopct(a):
    def my_autopct(pct):
        total = sum(a)
        val = int(round(pct * total / 100.0))
        return '{p:.2f}% ({v:d})'.format(p=pct, v=val)
    return my_autopct


class Job:
    def __init__(self, name: str, includes=[], excludes=[]):
        self.name = name
        self.includes = includes
        self.excludes = excludes

    def __str__(self):
        return self.name


def get_job_condition_sql(job: Job) -> str:
    includes = job.includes
    excludes = job.excludes
    includes_sql = ' or '.join(["job like '%' || ? || '%'"] * len(includes))
    if not includes_sql:
        raise ValueError("includes_sql should not be empty")
    excludes_sql = ' and '.join(
        ["job not like '%' || ? || '%'"] *
        len(excludes))
    cond_sql = f'({includes_sql}) and ({excludes_sql})' if excludes_sql else f'({includes_sql})'
    return cond_sql
