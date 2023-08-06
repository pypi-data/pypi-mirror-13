try:  # pragma: no cover
    from celery import shared_task

    @shared_task()
    def run_check():
        from updater import check
        return check.run_check()
except ImportError:  # pragma: no cover
    pass
