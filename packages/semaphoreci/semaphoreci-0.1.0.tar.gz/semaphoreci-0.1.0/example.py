# from semaphoreci import orm
from semaphoreci import session

s = session.SemaphoreCI(auth_token='iHZZQCzZVZox82Db2LRn')
betamax = s.projects()[0]
# master = s.branches(betamax)[0]
# history = s.branch_history(betamax, master)
# builds = history['builds']
# info = s.build_information(betamax, master, builds[0])
# logs = s.build_log(betamax, master, builds[0])
#
# rebuild = s.rebuild_last_revision(betamax, master)
# stop_rebuild = s.stop_build(betamax, master, rebuild)

# ss = orm.SemaphoreCI(auth_token=s.auth_token)
# projects = list(ss.projects())
