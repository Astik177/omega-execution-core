import os
import sys
import aiohttp
import smtplib
import asyncio
import ssl

# =========================================================================================
# OMEGA CORE: THE APEX TUNNEL V3 (CLOUD OPTIMIZED) - Runs on GitHub Servers
# =========================================================================================

async def get_mx_record(domain):
    url = f"https://dns.google/resolve?name={domain}&type=MX"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if 'Answer' in data:
                    mx_records = []
                    for answer in data['Answer']:
                        parts = answer['data'].split()
                        priority = int(parts[0])
                        server = parts[1].rstrip('.')
                        mx_records.append((priority, server))
                    
                    mx_records.sort(key=lambda x: x[0])
                    print(f"[+] MX RESOLVED: Found server {mx_records[0][1]}")
                    return mx_records[0][1]
        print(f"[-] DNS FAILED: No 'Answer' key in Google DNS response for {domain}.")
        return None
    except Exception as e:
        print(f"[!] FATAL DoH Error: {e}")
        return None

def verify_email_smtp(email, mx_record):
    try:
        server = smtplib.SMTP(mx_record, 25, timeout=10)
        server.set_debuglevel(0) # Set to 1 for verbose output
        server.ehlo('mail.google.com')
        server.mail('verify@google.com')
        code, message = server.rcpt(email)
        server.quit()
        if code == 250:
            return "VERIFIED"
        return "REJECTED"
    except smtplib.SMTPConnectError:
        return "ERROR_CONNECTION_REFUSED"
    except smtplib.SMTPServerDisconnected:
        return "ERROR_SERVER_DISCONNECTED"
    except Exception:
        return "ERROR_UNKNOWN"

async def omega_cloud_verify(email):
    print(f"[*] OMEGA CLOUD SWARM: Initiating verification for {email} from Microsoft Datacenter.")
    domain = email.split('@')[1]
    
    mx_record = await get_mx_record(domain)
    if not mx_record:
        return
        
    print(f"[*] Engaging SMTP Handshake with {mx_record}...")
    loop = asyncio.get_event_loop()
    status = await loop.run_in_executor(None, verify_email_smtp, email, mx_record)
    
    if status == "VERIFIED":
        print(f"\n[+] SUCCESS! EMAIL '{email}' IS 100% PREMIUM VERIFIED.\n")
    else:
        print(f"\n[-] FAILED. STATUS: {status} for email '{email}'.\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_email = sys.argv[1]
        asyncio.run(omega_cloud_verify(target_email))
    else:
        print("ERROR: Please provide an email to verify.")
        # Example for local testing if needed
        # asyncio.run(omega_cloud_verify("some.test@example.com"))