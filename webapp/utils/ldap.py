import os

from ldap3 import ALL, Connection, Server, Tls, NTLM, MODIFY_REPLACE
from ldap3.extend.microsoft.modifyPassword import ad_modify_password
from ldap3.extend.microsoft.addMembersToGroups import ad_add_members_to_groups
import ssl
from dotenv import load_dotenv

load_dotenv()

LDAP_SERVER = os.environ.get("LDAP_SERVER")
LDAP_USER = os.environ.get("LDAP_USER")
LDAP_PASS = os.environ.get("LDAP_PASS")
LDAP_DN = os.environ.get("LDAP_DN")
LDAP_DOMAIN = os.environ.get("LDAP_DOMAIN")
LDAP_GROUP = os.environ.get("LDAP_GROUP")


def get_ldap_connection():
    tls = Tls(validate=ssl.CERT_NONE)
    server = Server(LDAP_SERVER, get_info=ALL, port=636, use_ssl=True, tls=tls)
    conn = Connection(
        server,
        user=f"{LDAP_DOMAIN}\\{LDAP_USER}",
        password=LDAP_PASS,
        authentication=NTLM,
        auto_bind=True,
    )
    return conn


def ldap_exists(username):
    conn = get_ldap_connection()
    conn.search(LDAP_DN, f"(sAMAccountName={username})", attributes=["sAMAccountName"])
    conn.unbind()
    return len(conn.entries) > 0


def create_ldap_user(username, password):
    conn = get_ldap_connection()
    user_attributes = {
        "objectClass": ["top", "person", "organizationalPerson", "user"],
        "cn": username,
        "sAMAccountName": username,
        "userPrincipalName": f"{username}@{LDAP_DOMAIN}",
        "displayName": username,
    }
    # Create the user
    conn.add(f"cn={username}," + LDAP_DN, attributes=user_attributes)
    # Set the password
    ad_modify_password(conn, f"cn={username}," + LDAP_DN, password, None)
    # Enable the user
    conn.modify(
        f"cn={username}," + LDAP_DN, {"userAccountControl": [(MODIFY_REPLACE, [512])]}
    )

    conn.unbind()
    return conn.result["description"] == "success"

def add_to_group(username, group):
    conn = get_ldap_connection()
    ad_add_members_to_groups(conn, f"cn={username}," + LDAP_DN, [f"cn={group}," + LDAP_DN])
    conn.unbind()
    return conn.result["description"] == "success"

def change_ldap_password(username, password):
    conn = get_ldap_connection()
    ad_modify_password(conn, f"cn={username}," + LDAP_DN, password, None)
    conn.unbind()
    return conn.result["description"] == "success"
