# Investigation

## Disk Check

Filesystem usage was checked with:

df -h /

## Log Investigation

Large log directories were identified with:

du -xh /var/log --max-depth=2 | sort -h

The investigation showed:

- /var/log/devops-demo: approximately 513 MB
- /var/log total: approximately 842 MB

Individual files were then inspected with:

ls -lah /var/log/devops-demo
du -ah /var/log/devops-demo | sort -h

The large log generation was isolated to the DevOps demo application log directory.
