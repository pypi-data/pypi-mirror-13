
from matterhorn import App

app = App(__name__)

app.add_plugin('/sync', 'mm_syncbot.syncbot.syncbot', token='asdada')

app.add_plugin('/github', 'mm_github.github.github')