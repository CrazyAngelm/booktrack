BookTrack — Quality Analysis Report (Task 2)
Assessed 14 May 2025 on Windows 11 + Python 3.11 (local venv)

1  Method (one‑pass, evidence captured)
Area	Tool / command	Evidence
Build & run	docker compose up --build → manual venv fallback	container logs, CLI output 
Maintainability	pytest --cov, mutmut, radon mi, ruff, flake8	coverage HTML, radon.txt, linters 
Reliability	curl /health, log tail, 60‑min ping loop	console output 
Performance	Locust 2.37.1 (50 VU, 2 min), LHCI autorun	locust_stats, LHCI fail log 
Security	bandit -r, trufflehog, docker scout quickview	bandit.html, secrets.json, scan log 

2  Snapshot of measured quality
Category	Target	Achieved	Status
Coverage	≥ 65 %	71 %	✅
Mutation score	≥ 70 %	Not measured (mutmut unsupported on Windows)	❌
Maintainability Index	≥ 70	Mean 84.1, 14/38 files < 70	⚠️
Lint warnings	0	> 150 (Flake8 F401, F403, E501…)	❌
Health endpoint	HTTP 200	404	❌
Uptime evidence	≥ 99 %	Not monitored	❌
API mean RT (50 Mb/s)	≤ 2 000 ms	584 ms	✅
API 95‑th RT	≤ 2 000 ms	3 600 ms	❌
Lighthouse score	≥ 90	Run failed (no Chrome / config)	❌
Bandit high findings	0	2 HIGH, 1 MED	❌
Secrets in repo	0	Numerous hits (trufflehog)	❌

3  Key observations
Build pipeline is brittle – Docker fails (shell syntax + Nginx upstream), manual run needs logs/audit.log stub. 


Unit‑test base is solid (71 %), but mutation coverage and MI vary; CRUD & router modules are the worst offenders. 


No /health route ⇒ reliability cannot be proven; logging is present. 


Performance acceptable on average, but long tail > 3 s hints at heavy queries or missing indices. 


Security: shell‑based subprocess and un‑defused xmlrpc.client flagged as HIGH; secrets committed; image scan skipped. 


4  Recommendations (actionable, ranked)
Fix runtime baseline:

correct run_backend.sh / run_frontend.sh syntax;

add depends_on & correct upstream in nginx.conf; commit logs/ dir creation.

Reliability: implement GET /health (200 OK) and wire to UptimeRobot; keep log rotation.

Maintainability:

split large CRUD/router functions, add doc‑strings → raise MI < 70 files;

enable mutmut in CI (Linux) or switch to Cosmic‑Ray;

clean unused/wildcard imports, trim long lines; harmonise Ruff & Flake8 rules.

Performance: profile endpoints above 2 s (95‑th), add DB indices or caching; retest Locust.

Security:

replace subprocess(shell=True) with arg‑lists; patch XML parsing via defusedxml;

purge leaked secrets, add pre‑commit trufflehog;

scan Docker image after it builds successfully.

5  Conclusion
The project meets 2 / 11 stated thresholds (test coverage, mean API latency). The remaining gaps are all fixable with low‑to‑moderate effort (≈ 3–5 developer‑days). Implementing the five recommendations above will bring BookTrack to the required quality gate for Maintainability, Reliability, Performance and Security.