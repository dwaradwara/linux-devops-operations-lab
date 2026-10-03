# Root Cause

The new application release changed the internal listening port from 8000 to 9000.

The existing Docker port mapping and Nginx upstream configuration still expected port 8000.

As a result, the container remained running but traffic could not reach the application process.

This created an application-level outage despite the container itself appearing healthy.
