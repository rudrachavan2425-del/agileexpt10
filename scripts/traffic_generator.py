#!/usr/bin/env python3
"""
Traffic Generator for Placement Management System
Generates continuous, realistic HTTP traffic (browsing, student logins, searches,
applications, company logins, and occasional 404/401 errors) to populate Prometheus
metrics and provide dynamic, live Grafana dashboards.
"""

import argparse
import random
import time
import requests
from urllib.parse import urljoin

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
]

SEARCH_QUERIES = ['Python', 'Docker', 'Cloud', 'Data', 'Backend', 'Full Stack', 'Bengaluru', 'Remote']


def extract_csrf_token(html_text: str) -> str:
    """Extract CSRF token from HTML form if present."""
    import re
    match = re.search(r'name=["\']csrf_token["\'][^>]*?value=["\']([^"\']+)["\']', html_text)
    if match:
        return match.group(1)
    return ''


def simulate_traffic(base_url: str, delay: float, max_requests: int = None):
    print(f"[*] Starting Placement System Traffic Generator against {base_url}")
    print(f"[*] Request interval: {delay}s | Press Ctrl+C to terminate.")
    print("-" * 70)

    count = 0
    sessions = {
        'guest': requests.Session(),
        'student': requests.Session(),
        'company': requests.Session(),
        'admin': requests.Session(),
    }

    for name, s in sessions.items():
        s.headers.update({'User-Agent': random.choice(USER_AGENTS)})

    # Log in student session
    try:
        login_page = sessions['student'].get(urljoin(base_url, '/auth/login'), timeout=5)
        csrf = extract_csrf_token(login_page.text)
        sessions['student'].post(
            urljoin(base_url, '/auth/login'),
            data={'email': 'aarav.sharma@campus.edu', 'password': 'Student@123', 'csrf_token': csrf},
            timeout=5
        )
    except Exception as e:
        print(f"[!] Warning: Initial student login failed: {e}")

    # Log in company session
    try:
        login_page = sessions['company'].get(urljoin(base_url, '/auth/login'), timeout=5)
        csrf = extract_csrf_token(login_page.text)
        sessions['company'].post(
            urljoin(base_url, '/auth/login'),
            data={'email': 'recruiting@google.com', 'password': 'Company@123', 'csrf_token': csrf},
            timeout=5
        )
    except Exception as e:
        print(f"[!] Warning: Initial company login failed: {e}")

    # Log in admin session
    try:
        login_page = sessions['admin'].get(urljoin(base_url, '/auth/login'), timeout=5)
        csrf = extract_csrf_token(login_page.text)
        sessions['admin'].post(
            urljoin(base_url, '/auth/login'),
            data={'email': 'admin@placement.com', 'password': 'Admin@123', 'csrf_token': csrf},
            timeout=5
        )
    except Exception as e:
        print(f"[!] Warning: Initial admin login failed: {e}")

    actions = [
        ('guest', 'GET', '/'),
        ('guest', 'GET', '/health'),
        ('guest', 'GET', '/metrics'),
        ('student', 'GET', '/student/dashboard'),
        ('student', 'GET', '/student/jobs'),
        ('student', 'GET', '/student/profile'),
        ('company', 'GET', '/company/dashboard'),
        ('admin', 'GET', '/admin/dashboard'),
        ('admin', 'GET', '/admin/companies'),
        ('admin', 'GET', '/admin/students'),
        ('admin', 'GET', '/admin/jobs'),
        ('admin', 'GET', '/admin/applications'),
        ('guest', 'GET', '/not-found-page-simulated'),  # 404 test
    ]

    while True:
        if max_requests and count >= max_requests:
            break

        count += 1
        sess_key, method, path = random.choice(actions)
        sess = sessions[sess_key]
        full_url = urljoin(base_url, path)

        # Occasionally add search params
        params = {}
        if path == '/student/jobs' and random.random() < 0.6:
            params['q'] = random.choice(SEARCH_QUERIES)
            if random.random() < 0.4:
                params['eligible_only'] = '1'

        # Occasionally simulate a failed login to trigger 401 / failed login metrics
        if random.random() < 0.08:
            try:
                res = sess.post(
                    urljoin(base_url, '/auth/login'),
                    data={'email': 'invalid.user@campus.edu', 'password': 'WrongPassword!'},
                    timeout=5
                )
                elapsed_ms = res.elapsed.total_seconds() * 1000
                print(f"[{count:04d}] POST /auth/login (bad auth) -> {res.status_code} ({elapsed_ms:.1f}ms)")
                time.sleep(delay)
                continue
            except Exception as e:
                print(f"[{count:04d}] Error: {e}")

        t0 = time.time()
        try:
            resp = sess.get(full_url, params=params, timeout=5)
            elapsed = (time.time() - t0) * 1000
            print(f"[{count:04d}] {sess_key.upper():<7} {method} {path} -> {resp.status_code} ({elapsed:.1f}ms)")
        except Exception as e:
            print(f"[{count:04d}] {sess_key.upper():<7} {method} {path} -> EXCEPTION: {e}")

        time.sleep(delay)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Placement System Traffic Generator")
    parser.add_argument('--url', default='http://localhost:5000', help="Target application URL")
    parser.add_argument('--delay', type=float, default=0.5, help="Delay between requests in seconds")
    parser.add_argument('--count', type=int, default=None, help="Stop after N requests (default: run forever)")
    args = parser.parse_args()

    try:
        simulate_traffic(args.url, args.delay, args.count)
    except KeyboardInterrupt:
        print("\n[*] Traffic generation stopped by user.")
