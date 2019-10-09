

def clustering(type, args):
    # Cluster and write modules to file
    if args.do_recalculate:
        cyto_mod_adj.cluster_cytokines(K=bestK['adj'])
        cyto_mod_abs.cluster_cytokines(K=bestK['abs'])
        tools.write_to_dill(os.path.join(args.paths['clustering'], 'cyto_mod_adj.dill'), cyto_mod_adj)
        tools.write_to_dill(os.path.join(args.paths['clustering'], 'cyto_mod_abs.dill'), cyto_mod_abs)
    else: # Read modules from file
        cyto_mod_adj = tools.read_from_dill(os.path.join(args.paths['clustering'], 'cyto_mod_adj.dill'))
        cyto_mod_abs = tools.read_from_dill(os.path.join(args.paths['clustering'], 'cyto_mod_abs.dill'))

    cyto_modules = {'adj': cyto_mod_adj, 'abs': cyto_mod_abs}

