# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2012 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import cgi
import logging
import os
import time
import urllib

from twisted.internet import defer

from trosnoth.gamerecording.achievementlist import availableAchievements
from trosnoth.network.networkDefines import serverVersion
from trosnoth.utils.twist import WeakLoopingCall
from trosnoth.web.site import PageSet, ServerState, Template
from trosnoth.version import fullVersion
from trosnoth import data

log = logging.getLogger(__name__)

DOCTYPE = ('<!DOCTYPE html>')
pages = PageSet()
pages.achievementDefs = availableAchievements

# <script src="https://browserid.org/include.js" type="text/javascript"></script>
# <script src="/login.js" type="text/javascript"></script>
#  <header class="clearfix">
#    <div id="logininfo">
#      <div class="info">Not signed in</div>
#      <div class="signin"><a href="javascript:loginButtonClicked()"><img
#          src="https://browserid.org/i/sign_in_blue.png"></a></div>
#    </div>
#  </header>
pageTemplate = Template('''%(docType)s
<html>
<head>
<title>%(title)s</title>
<link href="/style.css" rel="stylesheet" type="text/css">
%(headers)s
</head>
<body>
<div id="container">
  %(contents)s
</div>
%(footers)s
</body>
</html>
''', {
    'docType': DOCTYPE,
    'title': 'Trosnoth server',
    'headers': '',
    'contents': '',
    'footers': '',
})

sendRequestJS = '''
  function newXMLHttpRequest() {
    if (window.XMLHttpRequest) {
        return new XMLHttpRequest();
    } else {
      return new ActiveXObject("Microsoft.XMLHTTP");
    }
  }
  function sendRequest(url, onSucceed, onFailure, method) {
    if (!method) method = 'GET';
    var xmlhttp = newXMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (xmlhttp.readyState == 4) {
        if (xmlhttp.status == 200) {
          onSucceed(xmlhttp.responseText);
        } else {
          onFailure(xmlhttp.status);
        }
      }
    };
    xmlhttp.open(method, url, true);
    xmlhttp.send();
  }
'''

timerJS = '''
  function Timer(initial, factor, maximum) {
    var value = initial;
    this.reset = function() {
      value = initial;
    };
    this.increment = function() {
      value *= factor;
      if (value > maximum) {
        value = maximum;
      }
    };
    this.getValue = function() {
      return value;
    }
  }
'''

@pages.addPage('/')
def home(state, request):
    return pageTemplate.apply(
        title=cgi.escape(state.getName()),
        contents='''
  <h1>%(serverName)s</h1>
  <a href="/play"><img src="/data/playnow" alt="Play now!"></a>

  <div id="message"></div>
  <div class="scoreboard" id="scoreboard" style="display:none">
    <div class="board_title">
      Game In Progress
    </div>
    <div class="zone_progress">
      <table width="100%%">
        <tr id="zone_progress_row">
          <td colspan="7" class="team1">-</td>
          <td colspan="3" class="neutral"></td>
          <td colspan="7" class="team2">-</td>
        </tr>
      </table>
    </div>
    <div class="team_tally">
        <div class="team_name">Blue Team</div>
        <div class="team_score" id="team1_score">0</div>
    </div>
    <div class="countdown">
        <div class="time_remaining">--:--</div>
        remaining
    </div>
    <div class="team_tally">
        <div class="team_name">Red Team</div>
        <div class="team_score" id="team2_score">0</div>
    </div>
    <div class="scoreboard_explanation">
      * 2 points awarded for capturing enemy zone, 1 point for neutral zone.
    </div>
  </div>

  <nav class="bottom_menu">
    <a href="/players">Player registry</a>
  </nav>
''' % {
    'serverName': cgi.escape(state.getName()),
}, footers=r'''
<script type="text/javascript">
  %(sendRequest)s
  %(timer)s

  function setText(elementId, text) {
    var element = document.getElementById(elementId);
    var txtNode = document.createTextNode(text);
    element.innerHTML = '';
    element.appendChild(txtNode);
  }

  function score(score1, score2, blueZones, greyZones, redZones) {
    document.getElementById('scoreboard').style.display = 'inherit';
    setText('team1_score', score1);
    setText('team2_score', score2);

    var rowHtml = '';
    if (blueZones > 0) {
        rowHtml += '<td colspan="' + blueZones + '" class="team1">';
        rowHtml += blueZones + '</td>';
    }
    if (greyZones > 0) {
        rowHtml += '<td colspan="' + greyZones + '" class="neutral">';
        rowHtml += greyZones + '</td>';
    }
    if (redZones > 0) {
        rowHtml += '<td colspan="' + redZones + '" class="team2">';
        rowHtml += redZones + '</td>';
    }
    document.getElementById('zone_progress_row').innerHTML = rowHtml;
  }

  function hideScoreboard() {
    document.getElementById('scoreboard').style.display = 'none';
  }
  function message(text) {
    document.getElementById('message').style.display = 'inherit';
    setText('message', text);
  }
  function hideMessage() {
    document.getElementById('message').style.display = 'none';
  }

  function connectionLost() {
    setText('team1_score', '?');
    setText('team2_score', '?');
    rowHtml = '<td colspan="7" class="team1">-</td>'
    rowHtml += '<td colspan="3" class="neutral"></td>'
    rowHtml += '<td colspan="7" class="team2">-</td>'
    document.getElementById('zone_progress_row').innerHTML = rowHtml;
  }

  var httpRequest;
  var retryCount = 0;
  function readyStateChange() {
    var readyState = httpRequest.readyState;
    if (readyState == 3) {
      if (httpRequest.status == 200) {
        retryCount = 0;
        var text = httpRequest.responseText;
        var i = text.lastIndexOf('\n');
        if (i > httpRequest.readTo) {
          text = text.substring(httpRequest.readTo, i);
          httpRequest.readTo = i;
          eval(text);
        }
      }
    } else if (readyState == 4) {
      if (httpRequest.status == 200) {
        retryCount = 0;
        var text = httpRequest.responseText;
        var i = text.lastIndexOf('\n');
        if (i > httpRequest.readTo) {
          text = text.substring(httpRequest.readTo, i);
          httpRequest.readTo = i;
          eval(text);
        }
        makeRequest();
      } else {
        connectionLost();
        setTimeout(makeRequest, retryCount + 1000);
        retryCount = retryCount * 1.5 + 1000;
        if (retryCount > 1000 * 60 * 5) {
          retryCount = 1000 * 60 * 5;
        }
      }
    }
  }
  function makeRequest() {
     httpRequest = newXMLHttpRequest();
     httpRequest.readTo = 0;
     httpRequest.overrideMimeType('text/xml');
     httpRequest.onreadystatechange = readyStateChange;
     // Math.random() is to avoid browser blocking if the page is open twice.
     httpRequest.open('GET', '/ajax/homepipe?r=' + Math.random(), true);
     httpRequest.send(null);
  }

  makeRequest();
</script>''' % {
    'sendRequest': sendRequestJS,
    'timer': timerJS,
})

@pages.addPage('/ajax/homepipe')
@defer.inlineCallbacks
def homepipe(state, request):
    sendData = state.getInitialEvents()
    request.write(sendData)
    while True:
        s = yield state.waitForEvent()
        if s is not None:
            request.write(s)

@pages.addPage('/login.js')
def loginjs(state, request):
    request.setHeader('Content-Type', 'text/javascript')
    return '''
function loginButtonClicked() {
    navigator.id.get(function(assertion) {
        if (assertion) {
            // We really need to send the assertion to the server to get it
            // verified.
            loggedIn();
        } else {
            // something went wrong!  the user isn't logged in.
            loggedOut();
        }
    });
}

function setSessions(val) {
  navigator.id.sessions = val ? val : [ ];
}

function loggedIn(email) {
  setSessions([ { email: email } ]);

  document.getElementById("logininfo").innerHTML = '<div class="info">Signed in</div>';
}

function loggedOut() {
  setSessions();
  document.getElementById("logininfo").innerHTML = '<div class="info">Not signed in</div><div class="signin"><a href="javascript:loginButtonClicked()"><img src="https://browserid.org/i/sign_in_blue.png"></a></div>';
}
'''

##container {
#  margin: 45px auto 0;
@pages.addPage('/style.css')
def style(state, request):
    request.setHeader('Content-Type', 'text/css')
    return '''
header {
    background-color: #eeeeee;
    border-bottom: 2px solid rgba(200, 230, 255, 0.5);
    box-shadow: 0 1px 8px rgba(0, 0, 64, 0.6);
    color: #606060;
    display: block;
    height: 30px;
    left: 0;
    opacity: 0.8;
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 10;
}

h1 {
  color: #000060;
  font-family: Junction, Verdana, Helvetica, sans-serif;
  font-size: 36px;
  text-align: center;
  text-shadow: #c0c0c0 1px 1px 1px;
}

header h1 {
  margin-top: 0px;
}

h1 a {
  text-decoration: none;
}
h1 a:visited {
  color: #000060;
}
h1 a:hover {
  color: #8080c0;
}

h2 {
  color: #000000;
  font-family: Junction, Verdana, Helvetica, sans-serif;
  font-size: 24px;
  text-align: center;
  text-shadow: #c0c0c0 1px 1px 1px;
}

.small {
  font-size: small;
}

#container {
  max-width: 680px;
  min-height: 100px;
  margin: 0 auto;
  background-image: url('/data/header');
  background-repeat:no-repeat;
  text-align: center;
  position: relative;
  padding-left: 60px;
  padding-right: 60px;
}

.scoreboard {
  width: 600px;
  min-height: 100px;
  margin: 0 auto;
  text-align: center;
  position: relative;
  border-radius: 20px;
  background-color: #333366;
  color: #ffffff;
  border-color: #fef;
}

.team_tally {
  padding: 5px;
  width: 185px;
  display: inline-block;
}
.countdown {
  width: 190px;
  padding: 5px;
  display: inline-block;
  font-size: 12px;
}
.board_title {
  padding: 5px;
  font-variant: small-caps;
}
.team_score {
  font-size: 40px;
}
.time_remaining {
  font-size: 30px;
}
.team1 {
  background-color: #00f;
}
.team2 {
  background-color: #f00;
}
.neutral {
  background-color: #888;
}
.zone_progress {
  padding: 4px;
}
.zone_progress table {
  table-layout: fixed;
  border: 1px solid white;
  border-radius: 4px;
}
.zone_progress table td {
  border-radius: 4px;
}
.scoreboard_explanation {
  font-size: 10px;
}

.achievement {
  display: inline-block;
  margin: 10px;
  width: 180px;
  vertical-align: top;
}

.achievement img {
  border: 1px solid black;
  padding: 0px;
}

.achievement_name {
  font-family: Junction, Verdana, Helvetica, sans-serif;
  margin-top: 5px;
}

a img {
  border: 0px none;
  margin: 2px;
}

#logininfo {
  float: right;
}

.info {
  display: inline-block;
  vertical-align: top;
  margin-top: 7px;
}

.signin {
  display: inline-block;
  margin-top: 2px;
}

.clearfix:after {
  clear: both;
  content: ".";
  display: block;
  height: 0;
  line-height: 0;
  visibility: hidden;
}

nav.bottom_menu {
    margin: 10px;
}
'''

@pages.addPage('/data/header')
def header(state, request):
    request.setHeader('Content-Type', 'image/png')
    if not hasattr(header, '_cachedImage'):
        header._cachedImage = open(data.getPath(data,
                'web', 'header.png'), 'rb').read()
    return header._cachedImage

@pages.addPage('/data/playnow')
def playNow(state, request):
    request.setHeader('Content-Type', 'image/png')
    if not hasattr(playNow, '_cachedImage'):
        playNow._cachedImage = open(data.getPath(data,
                'web', 'playnow.png'), 'rb').read()
    return playNow._cachedImage

@pages.addPage('/play')
def play(state, request):
    hostName = state.getHostName(request)
    homeAddress = state.getHomeAddress(request)
    return pageTemplate.apply(
        title=cgi.escape(state.getName()),
        contents='''
  <h1><a href="/">%(serverName)s</a></h1>
  <div id="playMsg">
    <noscript>
      The server is unable to detect whether the Trosnoth core is running
      because JavaScript is not enabled.<br>
      If you are running a Trosnoth version compatible with version %(version)s,
      <a href="%(playUrl)s">click here</a> to play on %(hostName)s.<br>
      You can download Trosnoth <a href="%(downloadUrl)s">here</a>.
    </noscript>
  </div>
''' % {
    'serverName': cgi.escape(state.getName()),
    'playUrl': 'http://localhost:8099/play?server=%s;port=%s;returnurl=%s;'
            'version=%s' % (urllib.quote(hostName), str(state.serverPort),
            urllib.quote(homeAddress), urllib.quote(serverVersion)),
    'downloadUrl': 'http://www.trosnoth.org/download',
    'hostName': hostName,
    'version': fullVersion,
}, footers='''
<script type="text/javascript">
  var playMsg = document.getElementById('playMsg');
  playMsg.innerHTML = 'Checking if Trosnoth is running...';

  var downloadHTML = 'You can download Trosnoth <a href="%(downloadUrl)s">';
  downloadHTML += 'here</a>.';

  %(sendRequest)s
  %(timer)s

  function TrosnothChecker() {
    var offTimer = new Timer(1000, 1.5, 5000);
    var onTimer = new Timer(2000, 1.5, 30000);
    var timeout = null;

    var success;
    var success1;
    var check;
    function badVersion(version) {
      var i = version.indexOf('\\n');
      if (i != -1) {
        version = version.substring(0, i);
      }
      var msg = '<p>You are running Trosnoth version ' + version
      msg += '. To play on this server, you must have version %(version)s '
      msg += 'or compatible.</p><p>' + downloadHTML + '</p>';
      playMsg.innerHTML = msg;
    }

    function versionMatch(versions) {
      var i = versions.indexOf('\\n');
      if (i == -1) {
        return false;
      }
      while (true) {
        versions = versions.substring(i + 1);
        var i = versions.indexOf('\\n');
        if (i == -1) {
          return (versions == "%(serverVersion)s");
        }
        if (versions.substring(0, i) == "%(serverVersion)s") {
          return true;
        }
      }
    }

    function scheduleSuccessRetry() {
      if (timeout) clearTimeout(timeout);
      offTimer.reset();
      timeout = setTimeout(check, onTimer.getValue());
      onTimer.increment();
    }

    this.success1 = success1 = function(text) {
      if (versionMatch(text)) {
        playMsg.innerHTML = 'Sending play request to Trosnoth core...';
        setTimeout(function() { window.location = '%(playUrl)s'; }, 1000);
      } else {
        badVersion(text);
      }
      scheduleSuccessRetry();
    };

    this.success = success = function(text) {
      if (versionMatch(text)) {
        var msg = 'Trosnoth core is running.<br>';
        msg += '<a href="%(playUrl)s">Click here</a> to play.';
        playMsg.innerHTML = msg;
      } else {
        badVersion(text);
      }
      scheduleSuccessRetry();
    };

    var error;
    this.error = error = function(code) {
      var msg = '<p>' + downloadHTML
      msg += '<br>To play on this server, you will need ';
      msg += 'version %(version)s or compatible.</p>';
      playMsg.innerHTML = msg;
      if (timeout) clearTimeout(timeout);
      onTimer.reset();
      timeout = setTimeout(check, offTimer.getValue());
      offTimer.increment();
    };

    this.check = check = function() {
      if (timeout) clearTimeout(timeout);
      sendRequest('http://localhost:8099/version', success, error);
    };
    this.check1 = function() {
      if (timeout) clearTimeout(timeout);
      sendRequest('http://localhost:8099/version', success1, error);
    };
  }

  var trosnothChecker = new TrosnothChecker();
  trosnothChecker.check1();

</script>
</body>
</html>
''' % {
    'version': fullVersion,
    'serverVersion': cgi.escape(serverVersion),
    'playUrl': 'http://localhost:8099/play?server=%s;port=%s;returnurl=%s;'
            'version=%s' % (urllib.quote(hostName), str(state.serverPort),
            urllib.quote(homeAddress), urllib.quote(serverVersion)),
    'downloadUrl': 'http://www.trosnoth.org/download',
    'hostName': hostName,
    'sendRequest': sendRequestJS,
    'timer': timerJS,
})

@pages.addPage('/players')
def playersList(state, request=None):
    players = state.getAllUsers()
    if players:
        players.sort(reverse=True, key=lambda p: p.lastSeen)
        lines = []
        for player in players:
            lines.append('<a href="/player?id=%s">%s</a> (%s)<br>' % (
                    urllib.quote(player.username), player.username,
                    formatTime(player.lastSeen)))
        playerList = '\n'.join(lines)
    else:
        playerList = '[ no players registered ]'

    return pageTemplate.apply(
        title=cgi.escape('%s :: Player Registry' % (state.getName(),)),
        contents='''
<h1><a href="/">%(serverName)s</a></h1>
<h2>Player Registry</h2>
%(playerList)s
''' % {
    'serverName': cgi.escape(state.getName()),
    'playerList': playerList,
})

@pages.addPage('/player')
def playerProfile(state, request):
    username = request.args.get('id', [None])[0]
    if username is None:
        return message(state, 'Bad request')
    user = state.getPlayer(username)
    if user is None:
        return message(state, 'Unknown user: %s' % (username,))

    title = '%s :: %s' % (state.getName(), username)
    achievements = []
    locked = set(pages.achievementDefs.byId)
    for achievement, status in user.achievements.iteritems():
        if status['unlocked']:
            try:
                name, description = pages.achievementDefs.getAchievementDetails(
                        achievement)
                locked.discard(achievement)
            except KeyError:
                # Achievement no longer exists.
                pass
            else:
                achievements.append((name, achievement, description))
    achievements.sort()
    achStrings = []
    for name, imgId, description in achievements:
        if not os.path.exists(data.getPath(data, 'achievements', '%s.png' %
                (imgId,))):
            imgId = 'default'

        achStrings.append(
            '<div class="achievement" title="%(description)s">'
            '<img src="/achievementimg?id=%(imgId)s" title="%(description)s">'
            '<div class="achievement_name">%(name)s</div></div>' % {
                'imgId': urllib.quote(imgId),
                'description': cgi.escape(description),
                'name': cgi.escape(name),
            }
        )

    lockedStrings = []
    for achId in sorted(locked):
        name, description = pages.achievementDefs.getAchievementDetails(achId)
        lockedStrings.append(
            '<div class="achievement" title="%(description)s">'
            '<img src="/achievementimg?id=default" title="%(description)s">'
            '<div class="achievement_name">%(name)s</div></div>' % {
                'description': cgi.escape(description),
                'name': cgi.escape(name),
            }
        )

    return pageTemplate.apply(
        title=cgi.escape(title),
        contents='''
<h1><a href="/">%(serverName)s</a></h1>
<h2>Player profile for %(username)s (%(nick)s)</h2>
<p>Last login: %(lastSeen)s</p>
<h3>Achievements unlocked: %(numUnlocked)s</h3>
%(achievements)s
<h3>Still locked:</h3>
%(locked)s
''' % {
    'serverName': cgi.escape(state.getName()),
    'username': username,
    'nick': user.getNick(),
    'numUnlocked': len(achStrings),
    'achievements': '\n'.join(achStrings) if achievements else 'none',
    'locked': '\n'.join(lockedStrings) if lockedStrings else 'none',
    'lastSeen': formatTime(user.lastSeen),
})

def formatTime(t):
    if t is None:
        return 'unknown'

    now = time.time()
    diff = now - t
    if diff < 5:
        return 'now'
    elif diff < 120:
        secs = int(diff + 0.5)
        return '%d second%s ago' % (secs, '' if secs == 1 else 's')
    elif diff < 3600:
        mins = int(diff / 60. + 0.5)
        return '%d minute%s ago' % (mins, '' if mins == 1 else 's')
    elif diff < 6 * 3600:
        hours, seconds = divmod(diff, 3600)
        mins = int(seconds / 60. + 0.5)
        return '%d hour%s and %d minute%s ago' % (int(hours), '' if
                hours == 1 else 's', mins, '' if mins == 1 else 's')
    elif diff < 24 * 3600:
        hours = int(diff / 3600. + 0.5)
        return '%d hour%s ago' % (hours, '' if hours == 1 else 's')
    elif diff < 7 * 24 * 3600:
        days, seconds = divmod(diff, 24 * 3600)
        hours = int(seconds / 3600. + 0.5)
        return '%d day%s and %d hour%s ago' % (int(days), '' if days == 1
                else 's', hours, '' if hours == 1 else 's')
    elif diff < 14 * 24 * 3600:
        days = int(diff / 24. / 3600 + 0.5)
        return '%d day%s ago' % (days, '' if days == 1 else 's')
    elif diff < 31 * 24 * 3600:
        weeks, seconds = divmod(diff, 7 * 24 * 3600)
        days = int(seconds / 24. / 3600 + 0.5)
        return '%d week%s and %d day%s ago' % (int(weeks), '' if weeks == 1
                else 's', days, '' if days == 1 else 's')
    elif diff < 365 * 24 * 3600:
        months, seconds = divmod(diff, 365 * 24 * 3600. / 12)
        days = int(seconds / 24. / 3600 + 0.5)
        return '%d month%s and %d day%s ago' % (int(months), '' if months == 1
                else 's', days, '' if days == 1 else 's')
    else:
        years = int(diff / 365.2425 / 24 / 3600 + 0.5)
        return '%d year%s ago' % (years, '' if years == 1 else 's')

@pages.addPage('/achievementimg')
def achievementImage(state, request):
    if not hasattr(achievementImage, '_cachedImages'):
        header._cachedImages = {None: None}

    id = request.args.get('id', [None])[0]
    if id in header._cachedImages:
        contents = header._cachedImages[id]
    else:
        try:
            contents = open(data.getPath(data, 'achievements', '%s.png' %
                    (id,)), 'rb').read()
        except IOError:
            contents = None
        header._cachedImages[id] = contents

    if contents is None:
        request.setResponseCode(404)
        return message(state, 'Not found')

    request.setHeader('Content-Type', 'image/png')
    return contents

def message(state, message, title=None):
    if title is None:
        title = state.getName()

    return pageTemplate.apply(
        title=cgi.escape(title),
        contents='''
<h1><a href="/">%(serverName)s</a></h1>
<div id="central_message">%(message)s</div>
''' % {
    'serverName': cgi.escape(state.getName()),
    'message': cgi.escape(message),
})

class WebServer(ServerState):
    def __init__(self, authFactory, serverPort):
        ServerState.__init__(self, pages)
        self.authFactory = authFactory
        self.serverPort = serverPort
        self.nextEventListeners = []
        self._loop = WeakLoopingCall(self, 'keepEventPipeAlive')
        self._loop.start(5, False)

        self.gameServer = None
        self.authFactory.onPrimaryGameChanged.addListener(
                self.gameServerChanged)

    def getName(self):
        return self.authFactory.settings.serverName

    def getHostName(self, req):
        '''
        Returns the host name of this server (for purpsose of connecting to
        Trosnoth games). This is taken from the settings file or (if no setting
        is given) from the request itself.
        '''
        hostName = self.authFactory.settings.hostName
        if not hostName:
            hostName = req.getRequestHostname()
        return hostName

    def getHomeAddress(self, req):
        '''
        Returns the home address of this server site, either from the settings
        file or (if no setting is given), from the request itself.
        '''
        homeAddress = self.authFactory.settings.serverName
        if not homeAddress:
            hostName = req.getRequestHostname()
            port = req.getHost().port
            if port == 80:
                homeAddress = 'http://%s/' % (hostName,)
            else:
                homeAddress = 'http://%s:%s/' % (hostName, port)
        return homeAddress

    def getPlayer(self, username):
        authMan = self.authFactory.authManager
        if authMan.checkUsername(username):
            return authMan.getUserByName(username)
        else:
            return None

    def getAchievements(self, player):
        return []

    def getAllUsers(self):
        authMan = self.authFactory.authManager
        return [authMan.getUserByName(u) for u in authMan.getAllUsernames()]

    def gameServerChanged(self, gameServer):
        if self.gameServer:
            world = self.gameServer.game.world
            world.onPlayerAdded.removeListener(self.playerCountChanged)
            world.onPlayerRemoved.removeListener(self.playerCountChanged)
            world.onGameStateChanged.removeListener(self.gameStateChanged)
            world.onTeamScoreChanged.removeListener(self.teamScoreChanged)
        self.gameServer = gameServer
        if gameServer:
            world = gameServer.game.world
            world.onPlayerAdded.addListener(self.playerCountChanged)
            world.onPlayerRemoved.addListener(self.playerCountChanged)
            world.onGameStateChanged.addListener(self.gameStateChanged)
            world.onTeamScoreChanged.addListener(self.teamScoreChanged)

        self.transmitEvent(self.getInitialEvents())

    def gameInProgress(self):
        game = self.gameServer.game
        return game.getGameState() in ('InProgress', 'Starting', 'Ended')

    def getPlayerCount(self):
        game = self.gameServer.game
        return len([p for p in game.world.players if not p.bot])

    def playerCountChanged(self, *args, **kwargs):
        if not self.gameInProgress():
            playerCount = self.getPlayerCount()
            playersString = '1 player' if playerCount == 1 else '%d players' % (
                    playerCount,)
            self.transmitEvent('message("%s in lobby.");' % (playersString,))

    def gameStateChanged(self, *args, **kwargs):
        self.transmitEvent(self.getInitialEvents())

    def getInitialEvents(self):
        if self.gameServer is None:
            return 'hideScoreboard();message("No running games on server.");\n'

        if not self.gameInProgress():
            playerCount = self.getPlayerCount()
            return 'hideScoreboard();message("%d players in lobby.");\n' % (
                    playerCount,)

        return 'hideMessage();%s\n' % (self.getScoreMessage(),)

    def teamScoreChanged(self, *args, **kwargs):
        self.transmitEvent(self.getScoreMessage())

    def getScoreMessage(self):
        world = self.gameServer.game.world
        blueTeam, redTeam = world.teams[:2]
        blueZones = blueTeam.numZonesOwned
        redZones = redTeam.numZonesOwned
        totalZones = len(world.zones)
        neutralZones = totalZones - blueZones - redZones

        return 'score(%d,%d,%d,%d,%d);' % (
            blueTeam.orbScore,
            redTeam.orbScore,
            blueZones,
            neutralZones,
            redZones,
        )

    def waitForEvent(self):
        d = defer.Deferred()
        self.nextEventListeners.append(d)
        return d

    def transmitEvent(self, jsCommand):
        listeners = self.nextEventListeners
        self.nextEventListeners = []
        for d in listeners:
            d.callback(jsCommand + '\n')

    def keepEventPipeAlive(self):
        '''
        To make sure that a reverse proxy doesn't close connections due to
        inactivity.
        '''
        self.transmitEvent('')

