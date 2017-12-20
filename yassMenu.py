################################################################################
# File:    yassMenu.py
# Author:  Ryan Yusko
# 
# Header and main menu definitions for the main program.
#
# @created 12/1/17
# @updated 12/1/17
################################################################################

################################################################################
# getHeader()
# Prints a fancy little header to welcome you to the screener.
#
# @created 12/1/17
def getHeader(ver, date):
  header = ""
  header += '____________________________________\n'
  header += '    _     _   __       __       __  \n'
  header += '    |    /    / |    /    )   /    )\n'
  header += '----|---/----/__|----\--------\-----\n'
  header += '    |  /    /   |     \        \    \n'
  header += '____|_/____/____|_(____/___(____/___\n'
  header += '     /    yet another stock screener\n'
  header += ' (_ /     v%g updated %s\n' % (ver, date)
  #header += '\n'
  return header
###################################################################  getHeader()

#//yassMenu.py