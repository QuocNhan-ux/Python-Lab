# Python + Cybersecurity Lab 3: Network Port Checker

**Time:** 45–60 minutes  
**Prerequisites:** Python 3.10+, basic Python functions and loops  
**Dependencies:** None (Python standard library only)

## Goal
Learn how TCP services can be reachable on a machine, and how a defender can inventory exposed ports. The tool checks a small set of TCP ports on **your own machine or private lab devices**. It does not identify vulnerabilities or prove services are secure.

**What you'll practice:** `socket`, `ipaddress`, functions, dictionaries, loops, `argparse`, exception handling, and return values.

## Experiment 1 — Make a known open port (10 minutes)

Open a terminal in this folder:

```powershell
python --version
python test_server.py
```

Keep this terminal open. The test server listens **only on your own computer** (`127.0.0.1`), TCP port `8765`.

Open a **second** terminal in this folder:

```powershell
python port_audit.py 127.0.0.1 --ports 8765 8766
```

Expected result: `8765` is `OPEN`. Port `8766` will normally say `closed / filtered` unless you have some other service listening there. Press **Ctrl+C** in the first terminal to stop the test server.

## Experiment 2 — Inspect the code (10 minutes)

1. Find `COMMON_PORTS`. Why use a dictionary rather than separate lists of port numbers and service names?
2. Find `check_port()`. What does `connect_ex() == 0` mean?
3. Change the timeout from `0.5` seconds to `1` second. How could this change scan speed when a host filters connections?
4. Find `local_ipv4()`. Why do we permit only local/private IPv4 networks?

## Experiment 3 — Explore your own lab (10 minutes)

Your Plex LXC previously showed the LAN IP `192.168.4.26`.
If it still has that address and you have permission, check its Plex port:

```powershell
python port_audit.py 192.168.4.26 --ports 32400 22 80
```

**Important:** The Proxmox host's port `8006` is on the **Proxmox host IP**, not necessarily on the Plex LXC's IP.

Try scanning the **host IP** separately with `--ports 8006` only if you know its address.

## Your coding challenges (15–20 minutes)

- **Beginner:** Add port `5432: "PostgreSQL"` and `3306: "MySQL"` to the `COMMON_PORTS` dictionary.
- **Intermediate:** Add a counter for the ports that are not open, and print both counters at the end.
- **Stretch:** Write scan results to a `scan_results.csv` file using the standard-library `csv` module (columns: host, port, service, status).

## Security interpretation

- An **open TCP port** means the checker completed a TCP connection. It does not mean the port is insecure.
- A **closed / filtered** result means the checker could not establish a connection; this simple tool does not distinguish a service that is down from one blocked by a firewall.
- A service name here is just a **common port label**, not verified service identification.
- Don't scan systems or networks without authorization.

## Publish your work

```powershell
git add .
git commit -m "Add network port checker lab"
git push
```

Use these commands from inside your existing Git repository, after reviewing the files to be committed. If you want this as a separate project, create a new repository first.
