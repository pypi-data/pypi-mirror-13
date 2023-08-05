from elex.api import Election


def add_election_hook(app):
    """
    Cache election API object reference after parsing args.
    """
    app.election = Election(
        testresults=app.pargs.test,
        liveresults=not app.pargs.not_live,
        is_test=False
    )
    if app.pargs.data_file:
        app.election.datafile = app.pargs.data_file
