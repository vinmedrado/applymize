def register_user(client, email, tenant):
    response = client.post("/api/auth/register", json={
        "tenant_name": tenant,
        "full_name": email.split("@")[0],
        "email": email,
        "password": "Strong123!",
        "skills": "Python, SQL, FastAPI, Docker",
        "seniority": "mid",
        "target_role": "Backend Python",
    })
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_tenant_isolation_cannot_access_other_tenant_job(client):
    h1 = register_user(client, "tenant1@test.com", "Tenant One")
    h2 = register_user(client, "tenant2@test.com", "Tenant Two")

    job = client.post("/api/jobs/", headers=h1, json={
        "title": "Private Job",
        "company": "TenantOne Co",
        "description": "Python SQL private tenant data",
        "requirements": "Python, SQL",
        "source": "manual",
        "external_id": "tenant-one-private-job",
    })
    assert job.status_code == 200, job.text
    job_id = job.json()["id"]

    own = client.get(f"/api/jobs/{job_id}", headers=h1)
    assert own.status_code == 200

    other = client.get(f"/api/jobs/{job_id}", headers=h2)
    assert other.status_code == 404

    other_match = client.post(f"/api/matching/jobs/{job_id}", headers=h2)
    assert other_match.status_code == 404

    other_apply = client.post("/api/applications/", headers=h2, json={"job_id": job_id, "status": "applied"})
    assert other_apply.status_code == 404


def test_list_jobs_only_returns_current_tenant(client):
    h1 = register_user(client, "tenant1list@test.com", "Tenant List One")
    h2 = register_user(client, "tenant2list@test.com", "Tenant List Two")

    client.post("/api/jobs/", headers=h1, json={
        "title": "Job Tenant 1",
        "company": "A",
        "description": "Python SQL",
        "source": "manual",
        "external_id": "list-tenant-1",
    })
    client.post("/api/jobs/", headers=h2, json={
        "title": "Job Tenant 2",
        "company": "B",
        "description": "Java Spring",
        "source": "manual",
        "external_id": "list-tenant-2",
    })

    jobs1 = client.get("/api/jobs/", headers=h1).json()
    jobs2 = client.get("/api/jobs/", headers=h2).json()

    assert len(jobs1) == 1
    assert len(jobs2) == 1
    assert jobs1[0]["title"] == "Job Tenant 1"
    assert jobs2[0]["title"] == "Job Tenant 2"
