#!/bin/bash
grep -rI "electrum\/" ../electrum-mona . 2> /dev/null | grep -v -e "\/locale\/" -e "README" -e "RELEASE-NOTES" -e "electrum\/{version\.ELECTRUM\_VERSION}" -e "\/issues\/4994" -e "\/issues\/5032" -e "\/pull\/5440"
grep -rI "import\ electrum " ../electrum-mona . 2> /dev/null | grep -v -e "\/locale\/" -e "README" -e "RELEASE-NOTES" -e "electrum\/{version\.ELECTRUM\_VERSION}" -e "\/issues\/4994" -e "\/issues\/5032" -e "\/pull\/5440"
grep -rI "import\ electrum\." ../electrum-mona . 2> /dev/null | grep -v -e "\/locale\/" -e "README" -e "RELEASE-NOTES" -e "electrum\/{version\.ELECTRUM\_VERSION}" -e "\/issues\/4994" -e "\/issues\/5032" -e "\/pull\/5440"
grep -rI "from\ electrum " ../electrum-mona . 2> /dev/null | grep -v -e "\/locale\/" -e "README" -e "RELEASE-NOTES" -e "electrum\/{version\.ELECTRUM\_VERSION}" -e "\/issues\/4994" -e "\/issues\/5032" -e "\/pull\/5440"
grep -rI "from\ electrum\." ../electrum-mona . 2> /dev/null | grep -v -e "\/locale\/" -e "README" -e "RELEASE-NOTES" -e "electrum\/{version\.ELECTRUM\_VERSION}" -e "\/issues\/4994" -e "\/issues\/5032" -e "\/pull\/5440"
grep -rI "electrum\.gui" ../electrum-mona . 2> /dev/null | grep -v -e "\/locale\/" -e "README" -e "RELEASE-NOTES" -e "electrum\/{version\.ELECTRUM\_VERSION}" -e "\/issues\/4994" -e "\/issues\/5032" -e "\/pull\/5440"
pytest electrum_mona/tests/ --full-trace
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
