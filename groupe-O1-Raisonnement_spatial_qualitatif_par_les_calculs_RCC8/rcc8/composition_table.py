COMPOSE = {

    "DC": {
        "DC": {"DC", "EC", "PO"},
        "EC": {"DC", "EC", "PO"},
        "PO": {"DC", "EC", "PO"},
        "EQ": {"DC", "EC", "PO"},
        "TPP": {"DC", "EC", "PO"},
        "TPPI": {"DC", "EC", "PO"},
        "NTPP": {"DC", "EC", "PO"},
        "NTPPI": {"DC", "EC", "PO"},
    },

    "EC": {
        "DC": {"DC", "EC", "PO"},
        "EC": {"DC", "EC", "PO", "TPP", "NTPP", "TPPI", "NTPPI"},
        "PO": {"DC", "EC", "PO"},
        "EQ": {"EC"},
        "TPP": {"DC", "EC", "PO", "TPP"},
        "TPPI": {"DC", "EC", "PO", "TPPI"},
        "NTPP": {"DC", "EC", "PO", "NTPP"},
        "NTPPI": {"DC", "EC", "PO", "NTPPI"},
    },

    "PO": {
        "DC": {"DC", "EC", "PO"},
        "EC": {"DC", "EC", "PO"},
        "PO": {"DC", "EC", "PO", "TPP", "TPPI", "NTPP", "NTPPI"},
        "EQ": {"PO"},
        "TPP": {"DC", "EC", "PO", "TPP"},
        "TPPI": {"DC", "EC", "PO", "TPPI"},
        "NTPP": {"DC", "EC", "PO", "NTPP"},
        "NTPPI": {"DC", "EC", "PO", "NTPPI"},
    },

    "EQ": {
        r: {r} for r in ["DC","EC","PO","EQ","TPP","TPPI","NTPP","NTPPI"]
    },

    "TPP": {
        "DC": {"DC", "EC", "PO"},
        "EC": {"DC", "EC", "PO", "TPP"},
        "PO": {"DC", "EC", "PO", "TPP"},
        "EQ": {"TPP"},
        "TPP": {"TPP", "NTPP"},
        "TPPI": {"DC", "EC", "PO"},
        "NTPP": {"NTPP"},
        "NTPPI": {"DC", "EC", "PO"},
    },

    "NTPP": {
        "DC": {"DC", "EC", "NTPP"},
        "EC": {"DC", "EC", "NTPP"},
        "PO": {"DC", "EC", "PO", "NTPP"},
        "EQ": {"NTPP"},
        "TPP": {"NTPP"},
        "TPPI": {"DC", "EC", "PO"},
        "NTPP": {"NTPP"},
        "NTPPI": {"DC", "EC", "PO"},
    },

    "TPPI": {
        "DC": {"DC", "EC", "PO"},
        "EC": {"DC", "EC", "PO", "TPPI"},
        "PO": {"DC", "EC", "PO", "TPPI"},
        "EQ": {"TPPI"},
        "TPP": {"DC", "EC", "PO"},
        "TPPI": {"TPPI", "NTPPI"},
        "NTPPI": {"NTPPI"},
    },

    "NTPPI": {
        "DC": {"DC", "EC", "PO"},
        "EC": {"DC", "EC", "PO", "NTPPI"},
        "PO": {"DC", "EC", "PO", "NTPPI"},
        "EQ": {"NTPPI"},
        "TPP": {"DC", "EC", "PO"},
        "TPPI": {"NTPPI"},
        "NTPPI": {"NTPPI"},
    },
}