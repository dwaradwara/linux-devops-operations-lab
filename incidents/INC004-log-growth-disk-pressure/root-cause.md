# Root Cause

The application log directory did not initially have a managed rotation and retention policy for the simulated high-volume log.

This allowed a single log file to grow to approximately 512 MB.

Without log rotation, continued growth could eventually consume available filesystem capacity.
