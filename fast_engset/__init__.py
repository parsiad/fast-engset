"""Fast and accurate routines to compute various quantities in the Engset model."""

from ._fast_engset import (
    Algorithm,
    Status,
    blocking_prob,
    n_servers,
    n_sources,
    total_traffic,
    _hyp2f1,
)
