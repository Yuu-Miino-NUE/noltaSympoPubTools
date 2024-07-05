from noltaSympoPubTools.requestRevise import get_ritems

revise_items = get_ritems(
    revise_json="revise_items.json",
    pids={6000},
)

revise_items.dump_json(
    filename="yet_revise_items.json",
)
