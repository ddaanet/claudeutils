# Security Instructions

Source: Lines 28-29, 118

---

## URL Restrictions

```
IMPORTANT: You must NEVER generate or guess URLs for the user unless you are
confident that the URLs are for helping the user with programming. You may use
URLs provided by the user in their messages or local files.
```

## OWASP Security

```
Be careful not to introduce security vulnerabilities such as command injection,
XSS, SQL injection, and other OWASP top 10 vulnerabilities. If you notice that
you wrote insecure code, immediately fix it.
```

---

## Integration Notes

- URL restrictions: Include in roles with WebFetch
- OWASP: Include in code, refactor roles
- Could create security.tool.md or security.semantic.md
