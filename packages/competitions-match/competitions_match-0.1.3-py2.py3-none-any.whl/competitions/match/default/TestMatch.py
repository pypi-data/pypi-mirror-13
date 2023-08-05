# -*- coding: utf-8  -*-
"""Match simulator for tests."""

# Copyright (C) 2015 Alexander Jones
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from competitions.match.Match import Match


class TestMatch(Match):

    """A match simulator for tests."""

    def __init__(self, team1, team2):
        """Constructor.

        @param team1: The first (home) team
        @type team1: An object that can be converted to a string
        @param team2: The second (away) team
        @type team2: An object that can be converted to a string
        """
        self.team1 = team1
        self.team2 = team2
        self.score1 = ''
        """The score for team1."""
        self.score2 = ''
        """The score for team2."""

    def __unicode__(self):
        """Return a unicode representation of the match.

        This will be of the form "<team1> <score1> - <score2> <team2>".
        @return: The match as a unicode string
        @rtype: unicode
        """
        return '{0} {1} - {2} {3}'.format(self.team1, self.score1,
                                          self.score2, self.team2)

    def __str__(self):
        """Return a str representation of the match.

        The format of the string is the same as that returned by __unicode__,
        except that it is a str object instead of a unicode object.
        @return: The match as a str
        @rtype: str
        """
        return str(self.__unicode__())

    def score_str(self):
        """Return the score of the match as a string.

        @return: The score of the match.
        @rtype: str
        """
        return '{0}-{1}'.format(self.score1, self.score2)

    def play(self):
        """Play the match.

        This simulator will always result in a 5-0 win for team1.
        @return: The winner (or None if the result is a draw)
        @rtype: An object that can be converted to a string or NoneType
        """
        self.score1 = 5
        self.score2 = 0
        self.winner = self.team1
        self.loser = self.team2
        return self.winner
