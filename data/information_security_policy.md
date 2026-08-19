---
title: "Synthetix Global Inc. Information Security & Data Privacy Policy"
document_id: "POL-SEC-2026-004"
version: "4.1"
status: "Approved"
effective_date: "2026-02-01"
review_cycle: "Annual"
next_review_date: "2027-02-01"
classification: "Internal Restricted"
owner: "Information Security Office (CISO)"
document_type: "Policy"
category: "Information Security"
subcategory: "Data Privacy and Cybersecurity"
audience:
  - Employees
  - Contractors
  - Consultants
  - Third-Party Service Providers
company: "Synthetix Global Inc."
department: "Information Security Office"
compliance_standards:
  - ISO/IEC 27001:2022
  - SOC 2 Type II
  - GDPR
  - CCPA
security_domains:
  - Data Classification
  - Identity and Access Management
  - Endpoint Security
  - Incident Response
  - Secure Software Development
  - Compliance Auditing
data_classification_levels:
  - Public
  - Internal
  - Confidential
  - Restricted
confidentiality: "Internal Restricted"
approval_authority: "Chief Information Security Officer (CISO)"
policy_region: "Global"
language: "en-US"
risk_level: "High"
retention_period: "Active while superseded; archive for 7 years after retirement"
source_system: "Policy Management System"
last_updated: "2026-02-01"
keywords:
  - information security
  - data privacy
  - cybersecurity
  - GDPR
  - CCPA
  - ISO 27001
  - SOC 2
  - IAM
  - MFA
  - incident response
  - SSDLC
  - endpoint security
tags:
  - Security
  - Privacy
  - Compliance
  - Governance
  - Risk Management
---

# Synthetix Global Inc. — Information Security & Data Privacy Policy

**Document ID:** POL-SEC-2026-004  
**Version:** 4.1  
**Compliance Standard:** ISO/IEC 27001:2022, SOC 2 Type II, GDPR, CCPA  
**Effective Date:** February 1, 2026  
**Classification:** Internal Restricted  
**Owner:** Information Security Office (CISO)  

---

## 1. Objective and Scope

This policy outlines mandatory cybersecurity safeguards and privacy protocols required to protect Synthetix Global systems, customer data, and intellectual property against unauthorized access, loss, data corruption, or compromise.

---

## 2. Data Classification Matrix

All corporate and client data is categorized into four distinct classification levels:

| Tier | Classification | Examples | Handling & Encryption Requirements |
| :--- | :--- | :--- | :--- |
| **L1** | **Public** | Marketing collateral, published whitepapers, open-source repositories. | No special encryption required; standard publication review. |
| **L2** | **Internal** | Employee directories, internal wikis, general announcements. | TLS 1.3 in transit; role-based access control (RBAC). |
| **L3** | **Confidential** | Source code, financial forecasts, employee compensation data. | AES-256 at rest, TLS 1.3 in transit, strict RBAC + MFA. |
| **L4** | **Restricted / PII** | Customer production databases, encryption keys, PII/HIPAA data. | Zero-Trust access, KMS encryption, audit logging, dual authorization. |

---

## 3. Identity and Access Management (IAM)

### 3.1 Authentication Standards
- **Multi-Factor Authentication (MFA):** Mandatory for all corporate logins (Okta/Google Workspace) using FIDO2 hardware keys (YubiKey) or push authenticators (1Password, Okta Verify). SMS-based 2FA is **prohibited**.
- **Password Complexity:**
  - Minimum 16 characters for administrative accounts; 14 characters for standard accounts.
  - Must include uppercase, lowercase, numbers, and special characters.
  - Automated rotation required every 90 days for privileged service accounts.
  - Must be stored exclusively in the corporate password manager (1Password Enterprise).

### 3.2 Access Provisioning & Deprovisioning
- **Principle of Least Privilege (PoLP):** Employees are granted only the minimum access level necessary to perform their roles.
- **Offboarding Deprovisioning SLA:** Access to all systems must be revoked within **2 hours** of formal termination notice.

---

## 4. Endpoint Security & Device Management

### 4.1 Corporate Hardware Standards
- All laptops must be managed via Mobile Device Management (MDM - Jamf / Microsoft Intune).
- **Mandatory Configuration:**
  - Full Disk Encryption enabled (FileVault on macOS / BitLocker on Windows).
  - Automatic screen lock after **5 minutes** of inactivity.
  - Endpoint Detection and Response (EDR - CrowdStrike Falcon) active and up-to-date.
  - Operating system automatic security updates enforced within 7 days of release.

### 4.2 Bring Your Own Device (BYOD)
- Personal devices accessing corporate email, Slack, or Google Workspace must enroll in the corporate MDM container profile.
- Storing unencrypted customer data or source code on personal local drives is strictly grounds for immediate disciplinary termination.

---

## 5. Security Incident Management & Breach Escalation

In the event of a suspected security breach, lost device, or ransomware encounter:

```
[ Step 1: Detect & Isolate ]
Disconnect device from network immediately (Wi-Fi / Ethernet).
        │
        ▼
[ Step 2: Emergency Alert ]
Notify CISO Incident Hotline: +1-888-999-SECU | Slack: #incident-emergency
        │
        ▼
[ Step 3: Triage & Containment ]
SOC Team assumes control, captures memory dump, and assesses blast radius.
        │
        ▼
[ Step 4: Regulatory Notification ]
Legal initiates GDPR/CCPA notification within the mandatory 72-hour window.
```

---

## 6. Secure Software Development Lifecycle (SSDLC)

1. **Code Reviews:** All pull requests targeting `main` or `release/*` require at least two senior peer approvals.
2. **Automated SAST/DAST:** CI/CD pipelines automatically reject builds failing static code analysis (SonarQube) or container image vulnerability scans (Snyk/Trivy).
3. **Secret Scanning:** Hardcoding API keys, private keys, or passwords in Git repositories is strictly prohibited; pre-commit hooks (GitGuardian) are enforced.

---

## 7. Compliance Verification & Audits

Internal audits are performed quarterly. Non-compliance with Information Security policies exposes the organization to legal penalties and severe brand risk, and will result in disciplinary action up to termination and legal prosecution.
