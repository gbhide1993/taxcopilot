# TaxCopilot Installation Guide

## System Requirements

* Windows / Mac / Linux
* Docker Desktop installed
* Minimum 8 GB RAM recommended
* 10 GB free disk space

---

## Step 1 — Start the System

Open terminal in the TaxCopilot folder and run:

docker compose up -d

This will start:

* PostgreSQL database
* Backend API
* Frontend UI
* AI inference server

Wait about **30–60 seconds** for all services to start.

---

## Step 2 — Install the AI Model

Run:

docker exec -it taxcopilot_ollama ollama pull phi

This downloads the AI model (~1.6 GB).
It only happens **once during first installation**.

---

## Step 3 — Load Demo Data

Run:

Get-Content taxcopilot_demo_dump.sql | docker exec -i taxcopilot_db psql -U postgres -d taxcopilot

This loads demo clients and notices so you can explore the system.

---

## Step 4 — Open TaxCopilot

Open your browser:

http://localhost:5173

---

## Default Login

Admin User
email: [admin@taxcopilot.local](mailto:admin@taxcopilot.local)
password: admin123

---

## Support

If you face issues during installation, contact the TaxCopilot support team.
