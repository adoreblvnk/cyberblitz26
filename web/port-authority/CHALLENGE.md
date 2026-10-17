The port's label pipeline sometimes assigns cargo to the wrong vessel. Bring the Berth Control release record and recover the final clearance token.

An operations memo was pinned to the portal:

    The public portal may preview remote label resources while operators prepare a shipment.

    Manifest drafts can be staged on the public portal and then imported by reference into the internal cargo queue. Operators should record the job trace shown by the internal system because failed render diagnostics are attached to that trace.

    Label profiles are maintained by the cargo automation team. If a profile fails to render, the worker stores the renderer event stream with the job record so operators can diagnose bad manifests later.

    Migration note: the cargo job API answers at api:9000 on the internal network. Its /v1/info record lists the active import and trace endpoints. The staging desk now requires the release record from Berth Control before it will sign a draft.

    Training manifests may still contain old clearance canaries such as PA-TRAINING-CLEARANCE-CANARY-NOT-FINAL. Those values are not final cargo tokens.

    Do not give customers direct access to the internal job API.

http://45.77.247.35:22012

http://5.223.64.53:22012

