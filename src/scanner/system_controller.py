Skip to content
careatomkarenterprises-ops
omkar-trade-desk
Repository navigation
Code
Issues
Pull requests
Agents
Actions
Projects
Security and quality
Insights
Settings
Hedge Fund Market Intelligence
Hedge Fund Market Intelligence #41
All jobs
Run details
run
succeeded now in 30s
Search logs
1s
1s
0s
19s
4s
1s
Run python execution_layer.py
  python execution_layer.py
  shell: /usr/bin/bash -e {0}
  env:
    pythonLocation: /opt/hostedtoolcache/Python/3.11.15/x64
    PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib/pkgconfig
    Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
    Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
    Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
    LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib
  
2026-04-17 11:58:18,278 - CRITICAL - ❌ IMPORT FAILED: system_controller not loading
2026-04-17 11:58:18,278 - ERROR - cannot import name 'NewsAgent' from 'src.scanner.edu_news_agent' (/home/runner/work/omkar-trade-desk/omkar-trade-desk/src/scanner/edu_news_agent.py)
Traceback (most recent call last):
  File "/home/runner/work/omkar-trade-desk/omkar-trade-desk/execution_layer.py", line 24, in <module>
    from src.scanner.system_controller import SystemController
  File "/home/runner/work/omkar-trade-desk/omkar-trade-desk/src/scanner/system_controller.py", line 12, in <module>
    from src.scanner.edu_news_agent import NewsAgent as CommodityAgent
ImportError: cannot import name 'NewsAgent' from 'src.scanner.edu_news_agent' (/home/runner/work/omkar-trade-desk/omkar-trade-desk/src/scanner/edu_news_agent.py)
2026-04-17 11:58:18,279 - INFO - 🚀 OMKAR TRADE DESK STARTED
2026-04-17 11:58:18,279 - INFO - 🕒 Time: 2026-04-17 11:58:18.279220
2026-04-17 11:58:18,279 - INFO - 🧪 Running Preflight System Check...
2026-04-17 11:58:18,279 - INFO - ✅ Preflight Check Passed
2026-04-17 11:58:18,279 - CRITICAL - ❌ SYSTEM STOPPED - CONTROLLER ISSUE
0s
Post job cleanup.
0s
Post job cleanup.
/usr/bin/git version
git version 2.53.0
Temporarily overriding HOME='/home/runner/work/_temp/1c041020-0dc2-4508-a051-66f5fe91a9d9' before making global git config changes
Adding repository directory to the temporary git global config as a safe directory
/usr/bin/git config --global --add safe.directory /home/runner/work/omkar-trade-desk/omkar-trade-desk
/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
http.https://github.com/.extraheader
/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
0s
