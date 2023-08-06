__version__ = "1.4.0"

description = """<p>QTodoTxt is a cross-platform UI client for todo.txt files
 (see <a href="http://todotxt.com">http://todotxt.com</a>)</p>

<p>Copyright &copy; David Elentok 2011</p>
<p>Copyright &copy; Matthieu Nantern 2013</p>

<h2>Links</h2>
<ul>
<li>Project Page: <a href="https://github.com/mNantern/QTodoTxt">https://github.com/mNantern/QTodoTxt</a></li>
</ul>

<h2>Credits</h2>

<ul>
    <li>Concept by <a href="http://ginatrapani.org/">Gina Trapani</a></li>
    <li>Icons by <a href="http://www.famfamfam.com/lab/icons/silk/">Mark James</a>
        and <a href="http://sekkyumu.deviantart.com/art/Developpers-Icons-63052312">Sekkyumu</a></li>
    <li>Original code by <a href="http://elentok.blogspot.com">David Elentok</a></li>
</ul>

<h2>License</h2>

<p>This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.</p>

<p>This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.</p>

<p>You should have received a copy of the GNU General Public License
along with this program.  If not, see
&lt;<a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>&gt;.</p>
"""

from PySide import QtGui


def _getAboutText():
    parts = ["<h1>About QTodoTxt %s</h1>\n" % __version__, description]
    return ''.join(parts)


def show(parent=None):
    text = _getAboutText()
    QtGui.QMessageBox.information(parent, 'About QTodoTxt', text)
