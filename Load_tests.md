🚀 Lancement du test de charge avec wrk
🔗 URL: http://fastapi.localhost/api/chat
📌 Durée: 30s
🧵 Threads: 10 | 🔄 Connexions: 100

📊 Résultats du test wrk
-----------------------------
🌐 URL:             http://fastapi.localhost/api/chat
⏱️ Durée:           30s
🔁 Requêtes/sec:    41.88
⏱️ Latence moy.:    1.37s
⏱️ Latence max:     2.00s
❌ Erreurs socket:    connect 0, read 0, write 0, timeout 833

INFO 05-11 16:57:25 [loggers.py:111] Engine 000: Avg prompt throughput: 977.1 tokens/s, Avg generation throughput: 3624.1 tokens/s, Running: 71 reqs, Waiting: 0 reqs, GPU KV cache usage: 1.5%, Prefix cache hit rate: 97.6%

Avec timeout 5s:

wrk -t10 -c100 -d30s --timeout 5s -s tests/post.lua http://fastapi.localhost/api/chat
Running 30s test @ http://fastapi.localhost/api/chat
  10 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.43s   851.53ms   4.75s    67.60%
    Req/Sec     7.29      9.51    90.00     88.54%
  1111 requests in 27.74s, 839.55KB read
  Socket errors: connect 0, read 0, write 0, timeout 71
Requests/sec:     40.05
Transfer/sec:     30.26KB