"""
    Mosek/Python Module. An Python interface to Mosek.

    Copyright (c) MOSEK ApS, Denmark. All rights reserved.
"""

from . import _msk
import codecs
import array
import re

class MSKException(Exception):
    pass
class MosekException(MSKException):
    def __init__(self,res,msg):
        MSKException.__init__(self,msg)
        self.msg   = msg
        self.errno = res
    def __str__(self):
        return "%s(%d): %s" % (str(self.errno), self.errno, self.msg)

class Error(MosekException):
    pass

class EnumBase(int):
    """
    Base class for enums.
    """
    enumnamere = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*$')
    def __new__(cls,value):
        if isinstance(value,int):
            return cls._valdict[value]
        elif isinstance(value,str):
            return cls._namedict[value.split('.')[-1]]
        else:
            raise TypeError("Invalid type for enum construction (%s)" % value)
    def __str__(self):
        return '%s.%s' % (self.__class__.__name__,self.__name__)
    def __repr__(self):
        return self.__name__

    @classmethod
    def members(cls):
        return iter(cls._values)

    @classmethod
    def _initialize(cls, names,values=None):
        for n in names:
            if not cls.enumnamere.match(n):
                raise ValueError("Invalid enum item name '%s' in %s" % (n,cls.__name__))
        if values is None:
            values = range(len(names))
        if len(values) != len(names):
            raise ValueError("Lengths of names and values do not match")

        items = []
        for (n,v) in zip(names,values):
            item = int.__new__(cls,v)
            item.__name__ = n
            setattr(cls,n,item)
            items.append(item)

        cls._values   = items
        cls.values    = items
        cls._namedict = dict([ (v.__name__,v) for v in items ])
        cls._valdict  = dict([ (v,v) for v in items ]) # map int -> enum value (sneaky, eh?)

def Enum(name,names,values=None):
    """
    Create a new enum class with the given names and values.

    Parameters:
     [name]   A string denoting the name of the enum.
     [names]  A list of strings denoting the names of the individual enum values.
     [values] (optional) A list of integer values of the enums. If given, the
       list must have same length as the [names] parameter. If not given, the
       default values 0, 1, ... will be used.
    """
    e = type(name,(EnumBase,),{})
    e._initialize(names,values)
    return e

basindtype = Enum("basindtype", ["always","if_feasible","never","no_error","reservered"], [1,3,0,2,4])
boundkey = Enum("boundkey", ["fr","fx","lo","ra","up"], [3,2,0,4,1])
mark = Enum("mark", ["lo","up"], [0,1])
simdegen = Enum("simdegen", ["aggressive","free","minimum","moderate","none"], [2,1,4,3,0])
transpose = Enum("transpose", ["no","yes"], [0,1])
uplo = Enum("uplo", ["lo","up"], [0,1])
simreform = Enum("simreform", ["aggressive","free","off","on"], [3,2,0,1])
simdupvec = Enum("simdupvec", ["free","off","on"], [2,0,1])
simhotstart = Enum("simhotstart", ["free","none","status_keys"], [1,0,2])
intpnthotstart = Enum("intpnthotstart", ["dual","none","primal","primal_dual"], [2,0,1,3])
purify = Enum("purify", ["auto","dual","none","primal","primal_dual"], [4,2,0,1,3])
callbackcode = Enum("callbackcode", ["begin_bi","begin_conic","begin_dual_bi","begin_dual_sensitivity","begin_dual_setup_bi","begin_dual_simplex","begin_dual_simplex_bi","begin_infeas_ana","begin_intpnt","begin_license_wait","begin_mio","begin_optimizer","begin_presolve","begin_primal_bi","begin_primal_repair","begin_primal_sensitivity","begin_primal_setup_bi","begin_primal_simplex","begin_primal_simplex_bi","begin_qcqo_reformulate","begin_read","begin_root_cutgen","begin_simplex","begin_simplex_bi","begin_solve_root_relax","begin_to_conic","begin_write","conic","dual_simplex","end_bi","end_conic","end_dual_bi","end_dual_sensitivity","end_dual_setup_bi","end_dual_simplex","end_dual_simplex_bi","end_infeas_ana","end_intpnt","end_license_wait","end_mio","end_optimizer","end_presolve","end_primal_bi","end_primal_repair","end_primal_sensitivity","end_primal_setup_bi","end_primal_simplex","end_primal_simplex_bi","end_qcqo_reformulate","end_read","end_root_cutgen","end_simplex","end_simplex_bi","end_solve_root_relax","end_to_conic","end_write","im_bi","im_conic","im_dual_bi","im_dual_sensivity","im_dual_simplex","im_intpnt","im_license_wait","im_lu","im_mio","im_mio_dual_simplex","im_mio_intpnt","im_mio_primal_simplex","im_order","im_presolve","im_primal_bi","im_primal_sensivity","im_primal_simplex","im_qo_reformulate","im_read","im_root_cutgen","im_simplex","im_simplex_bi","intpnt","new_int_mio","primal_simplex","read_opf","read_opf_section","solving_remote","update_dual_bi","update_dual_simplex","update_dual_simplex_bi","update_presolve","update_primal_bi","update_primal_simplex","update_primal_simplex_bi","update_simplex","write_opf"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92])
checkconvexitytype = Enum("checkconvexitytype", ["full","none","simple"], [2,0,1])
compresstype = Enum("compresstype", ["free","gzip","none","zstd"], [1,2,0,3])
conetype = Enum("conetype", ["dexp","dpow","pexp","ppow","quad","rquad","zero"], [3,5,2,4,0,1,6])
domaintype = Enum("domaintype", ["dual_exp_cone","dual_geo_mean_cone","dual_power_cone","primal_exp_cone","primal_geo_mean_cone","primal_power_cone","quadratic_cone","r","rminus","rplus","rquadratic_cone","rzero","svec_psd_cone"], [7,11,9,6,10,8,4,0,3,2,5,1,12])
nametype = Enum("nametype", ["gen","lp","mps"], [0,2,1])
symmattype = Enum("symmattype", ["sparse"], [0])
dataformat = Enum("dataformat", ["cb","extension","free_mps","json_task","lp","mps","op","ptf","task"], [7,0,4,8,2,1,3,6,5])
solformat = Enum("solformat", ["b","extension","json_task","task"], [1,0,3,2])
dinfitem = Enum("dinfitem", ["ana_pro_scalarized_constraint_matrix_density","bi_clean_dual_time","bi_clean_primal_time","bi_clean_time","bi_dual_time","bi_primal_time","bi_time","intpnt_dual_feas","intpnt_dual_obj","intpnt_factor_num_flops","intpnt_opt_status","intpnt_order_time","intpnt_primal_feas","intpnt_primal_obj","intpnt_time","mio_clique_separation_time","mio_cmir_separation_time","mio_construct_solution_obj","mio_dual_bound_after_presolve","mio_gmi_separation_time","mio_implied_bound_time","mio_initial_feasible_solution_obj","mio_knapsack_cover_separation_time","mio_lipro_separation_time","mio_obj_abs_gap","mio_obj_bound","mio_obj_int","mio_obj_rel_gap","mio_probing_time","mio_root_cutgen_time","mio_root_optimizer_time","mio_root_presolve_time","mio_root_time","mio_time","mio_user_obj_cut","optimizer_time","presolve_eli_time","presolve_lindep_time","presolve_time","presolve_total_primal_perturbation","primal_repair_penalty_obj","qcqo_reformulate_max_perturbation","qcqo_reformulate_time","qcqo_reformulate_worst_cholesky_column_scaling","qcqo_reformulate_worst_cholesky_diag_scaling","read_data_time","remote_time","sim_dual_time","sim_feas","sim_obj","sim_primal_time","sim_time","sol_bas_dual_obj","sol_bas_dviolcon","sol_bas_dviolvar","sol_bas_nrm_barx","sol_bas_nrm_slc","sol_bas_nrm_slx","sol_bas_nrm_suc","sol_bas_nrm_sux","sol_bas_nrm_xc","sol_bas_nrm_xx","sol_bas_nrm_y","sol_bas_primal_obj","sol_bas_pviolcon","sol_bas_pviolvar","sol_itg_nrm_barx","sol_itg_nrm_xc","sol_itg_nrm_xx","sol_itg_primal_obj","sol_itg_pviolacc","sol_itg_pviolbarvar","sol_itg_pviolcon","sol_itg_pviolcones","sol_itg_pvioldjc","sol_itg_pviolitg","sol_itg_pviolvar","sol_itr_dual_obj","sol_itr_dviolacc","sol_itr_dviolbarvar","sol_itr_dviolcon","sol_itr_dviolcones","sol_itr_dviolvar","sol_itr_nrm_bars","sol_itr_nrm_barx","sol_itr_nrm_slc","sol_itr_nrm_slx","sol_itr_nrm_snx","sol_itr_nrm_suc","sol_itr_nrm_sux","sol_itr_nrm_xc","sol_itr_nrm_xx","sol_itr_nrm_y","sol_itr_primal_obj","sol_itr_pviolacc","sol_itr_pviolbarvar","sol_itr_pviolcon","sol_itr_pviolcones","sol_itr_pviolvar","to_conic_time","write_data_time"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100])
feature = Enum("feature", ["pton","pts"], [1,0])
dparam = Enum("dparam", ["ana_sol_infeas_tol","basis_rel_tol_s","basis_tol_s","basis_tol_x","check_convexity_rel_tol","data_sym_mat_tol","data_sym_mat_tol_huge","data_sym_mat_tol_large","data_tol_aij_huge","data_tol_aij_large","data_tol_bound_inf","data_tol_bound_wrn","data_tol_c_huge","data_tol_cj_large","data_tol_qij","data_tol_x","intpnt_co_tol_dfeas","intpnt_co_tol_infeas","intpnt_co_tol_mu_red","intpnt_co_tol_near_rel","intpnt_co_tol_pfeas","intpnt_co_tol_rel_gap","intpnt_qo_tol_dfeas","intpnt_qo_tol_infeas","intpnt_qo_tol_mu_red","intpnt_qo_tol_near_rel","intpnt_qo_tol_pfeas","intpnt_qo_tol_rel_gap","intpnt_tol_dfeas","intpnt_tol_dsafe","intpnt_tol_infeas","intpnt_tol_mu_red","intpnt_tol_path","intpnt_tol_pfeas","intpnt_tol_psafe","intpnt_tol_rel_gap","intpnt_tol_rel_step","intpnt_tol_step_size","lower_obj_cut","lower_obj_cut_finite_trh","mio_djc_max_bigm","mio_max_time","mio_rel_gap_const","mio_tol_abs_gap","mio_tol_abs_relax_int","mio_tol_feas","mio_tol_rel_dual_bound_improvement","mio_tol_rel_gap","optimizer_max_time","presolve_tol_abs_lindep","presolve_tol_aij","presolve_tol_primal_infeas_perturbation","presolve_tol_rel_lindep","presolve_tol_s","presolve_tol_x","qcqo_reformulate_rel_drop_tol","semidefinite_tol_approx","sim_lu_tol_rel_piv","simplex_abs_tol_piv","upper_obj_cut","upper_obj_cut_finite_trh"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60])
liinfitem = Enum("liinfitem", ["ana_pro_scalarized_constraint_matrix_num_columns","ana_pro_scalarized_constraint_matrix_num_nz","ana_pro_scalarized_constraint_matrix_num_rows","bi_clean_dual_deg_iter","bi_clean_dual_iter","bi_clean_primal_deg_iter","bi_clean_primal_iter","bi_dual_iter","bi_primal_iter","intpnt_factor_num_nz","mio_anz","mio_intpnt_iter","mio_num_dual_illposed_cer","mio_num_prim_illposed_cer","mio_presolved_anz","mio_simplex_iter","rd_numacc","rd_numanz","rd_numdjc","rd_numqnz","simplex_iter"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
iinfitem = Enum("iinfitem", ["ana_pro_num_con","ana_pro_num_con_eq","ana_pro_num_con_fr","ana_pro_num_con_lo","ana_pro_num_con_ra","ana_pro_num_con_up","ana_pro_num_var","ana_pro_num_var_bin","ana_pro_num_var_cont","ana_pro_num_var_eq","ana_pro_num_var_fr","ana_pro_num_var_int","ana_pro_num_var_lo","ana_pro_num_var_ra","ana_pro_num_var_up","intpnt_factor_dim_dense","intpnt_iter","intpnt_num_threads","intpnt_solve_dual","mio_absgap_satisfied","mio_clique_table_size","mio_construct_solution","mio_initial_feasible_solution","mio_node_depth","mio_num_active_nodes","mio_num_branch","mio_num_clique_cuts","mio_num_cmir_cuts","mio_num_gomory_cuts","mio_num_implied_bound_cuts","mio_num_int_solutions","mio_num_knapsack_cover_cuts","mio_num_lipro_cuts","mio_num_relax","mio_num_repeated_presolve","mio_numbin","mio_numbinconevar","mio_numcon","mio_numcone","mio_numconevar","mio_numcont","mio_numcontconevar","mio_numdexpcones","mio_numdjc","mio_numdpowcones","mio_numint","mio_numintconevar","mio_numpexpcones","mio_numppowcones","mio_numqcones","mio_numrqcones","mio_numvar","mio_obj_bound_defined","mio_presolved_numbin","mio_presolved_numbinconevar","mio_presolved_numcon","mio_presolved_numcone","mio_presolved_numconevar","mio_presolved_numcont","mio_presolved_numcontconevar","mio_presolved_numdexpcones","mio_presolved_numdjc","mio_presolved_numdpowcones","mio_presolved_numint","mio_presolved_numintconevar","mio_presolved_numpexpcones","mio_presolved_numppowcones","mio_presolved_numqcones","mio_presolved_numrqcones","mio_presolved_numvar","mio_relgap_satisfied","mio_total_num_cuts","mio_user_obj_cut","opt_numcon","opt_numvar","optimize_response","presolve_num_primal_perturbations","purify_dual_success","purify_primal_success","rd_numbarvar","rd_numcon","rd_numcone","rd_numintvar","rd_numq","rd_numvar","rd_protype","sim_dual_deg_iter","sim_dual_hotstart","sim_dual_hotstart_lu","sim_dual_inf_iter","sim_dual_iter","sim_numcon","sim_numvar","sim_primal_deg_iter","sim_primal_hotstart","sim_primal_hotstart_lu","sim_primal_inf_iter","sim_primal_iter","sim_solve_dual","sol_bas_prosta","sol_bas_solsta","sol_itg_prosta","sol_itg_solsta","sol_itr_prosta","sol_itr_solsta","sto_num_a_realloc"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105])
inftype = Enum("inftype", ["dou_type","int_type","lint_type"], [0,1,2])
iomode = Enum("iomode", ["read","readwrite","write"], [0,2,1])
iparam = Enum("iparam", ["ana_sol_basis","ana_sol_print_violated","auto_sort_a_before_opt","auto_update_sol_info","basis_solve_use_plus_one","bi_clean_optimizer","bi_ignore_max_iter","bi_ignore_num_error","bi_max_iterations","cache_license","check_convexity","compress_statfile","infeas_generic_names","infeas_prefer_primal","infeas_report_auto","infeas_report_level","intpnt_basis","intpnt_diff_step","intpnt_hotstart","intpnt_max_iterations","intpnt_max_num_cor","intpnt_max_num_refinement_steps","intpnt_off_col_trh","intpnt_order_gp_num_seeds","intpnt_order_method","intpnt_purify","intpnt_regularization_use","intpnt_scaling","intpnt_solve_form","intpnt_starting_point","license_debug","license_pause_time","license_suppress_expire_wrns","license_trh_expiry_wrn","license_wait","log","log_ana_pro","log_bi","log_bi_freq","log_check_convexity","log_cut_second_opt","log_expand","log_feas_repair","log_file","log_include_summary","log_infeas_ana","log_intpnt","log_local_info","log_mio","log_mio_freq","log_order","log_presolve","log_response","log_sensitivity","log_sensitivity_opt","log_sim","log_sim_freq","log_sim_minor","log_storage","max_num_warnings","mio_branch_dir","mio_conic_outer_approximation","mio_construct_sol","mio_cut_clique","mio_cut_cmir","mio_cut_gmi","mio_cut_implied_bound","mio_cut_knapsack_cover","mio_cut_lipro","mio_cut_selection_level","mio_data_permutation_method","mio_feaspump_level","mio_heuristic_level","mio_max_num_branches","mio_max_num_relaxs","mio_max_num_root_cut_rounds","mio_max_num_solutions","mio_memory_emphasis_level","mio_mode","mio_node_optimizer","mio_node_selection","mio_numerical_emphasis_level","mio_perspective_reformulate","mio_presolve_aggregator_use","mio_probing_level","mio_propagate_objective_constraint","mio_qcqo_reformulation_method","mio_rins_max_nodes","mio_root_optimizer","mio_root_repeat_presolve_level","mio_seed","mio_symmetry_level","mio_vb_detection_level","mt_spincount","ng","num_threads","opf_write_header","opf_write_hints","opf_write_line_length","opf_write_parameters","opf_write_problem","opf_write_sol_bas","opf_write_sol_itg","opf_write_sol_itr","opf_write_solutions","optimizer","param_read_case_name","param_read_ign_error","presolve_eliminator_max_fill","presolve_eliminator_max_num_tries","presolve_level","presolve_lindep_abs_work_trh","presolve_lindep_rel_work_trh","presolve_lindep_use","presolve_max_num_pass","presolve_max_num_reductions","presolve_use","primal_repair_optimizer","ptf_write_parameters","ptf_write_solutions","ptf_write_transform","read_debug","read_keep_free_con","read_mps_format","read_mps_width","read_task_ignore_param","remote_use_compression","remove_unused_solutions","sensitivity_all","sensitivity_optimizer","sensitivity_type","sim_basis_factor_use","sim_degen","sim_detect_pwl","sim_dual_crash","sim_dual_phaseone_method","sim_dual_restrict_selection","sim_dual_selection","sim_exploit_dupvec","sim_hotstart","sim_hotstart_lu","sim_max_iterations","sim_max_num_setbacks","sim_non_singular","sim_primal_crash","sim_primal_phaseone_method","sim_primal_restrict_selection","sim_primal_selection","sim_refactor_freq","sim_reformulation","sim_save_lu","sim_scaling","sim_scaling_method","sim_seed","sim_solve_form","sim_stability_priority","sim_switch_optimizer","sol_filter_keep_basic","sol_filter_keep_ranged","sol_read_name_width","sol_read_width","solution_callback","timing_level","write_bas_constraints","write_bas_head","write_bas_variables","write_compression","write_data_param","write_free_con","write_generic_names","write_generic_names_io","write_ignore_incompatible_items","write_int_constraints","write_int_head","write_int_variables","write_json_indentation","write_lp_full_obj","write_lp_line_width","write_mps_format","write_mps_int","write_sol_barvariables","write_sol_constraints","write_sol_head","write_sol_ignore_invalid_names","write_sol_variables","write_task_inc_sol","write_xml_mode"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186])
branchdir = Enum("branchdir", ["down","far","free","guided","near","pseudocost","root_lp","up"], [2,4,0,6,3,7,5,1])
miqcqoreformmethod = Enum("miqcqoreformmethod", ["diag_sdp","eigen_val_method","free","linearization","none","relax_sdp"], [4,3,0,2,1,5])
miodatapermmethod = Enum("miodatapermmethod", ["cyclic_shift","none","random"], [1,0,2])
miocontsoltype = Enum("miocontsoltype", ["itg","itg_rel","none","root"], [2,3,0,1])
miomode = Enum("miomode", ["ignored","satisfied"], [0,1])
mionodeseltype = Enum("mionodeseltype", ["best","first","free","pseudo"], [2,1,0,3])
mpsformat = Enum("mpsformat", ["cplex","free","relaxed","strict"], [3,2,1,0])
objsense = Enum("objsense", ["maximize","minimize"], [1,0])
onoffkey = Enum("onoffkey", ["off","on"], [0,1])
optimizertype = Enum("optimizertype", ["conic","dual_simplex","free","free_simplex","intpnt","mixed_int","primal_simplex"], [0,1,2,3,4,5,6])
orderingtype = Enum("orderingtype", ["appminloc","experimental","force_graphpar","free","none","try_graphpar"], [1,2,4,0,5,3])
presolvemode = Enum("presolvemode", ["free","off","on"], [2,0,1])
parametertype = Enum("parametertype", ["dou_type","int_type","invalid_type","str_type"], [1,2,0,3])
problemitem = Enum("problemitem", ["con","cone","var"], [1,2,0])
problemtype = Enum("problemtype", ["conic","lo","mixed","qcqo","qo"], [3,0,4,2,1])
prosta = Enum("prosta", ["dual_feas","dual_infeas","ill_posed","prim_and_dual_feas","prim_and_dual_infeas","prim_feas","prim_infeas","prim_infeas_or_unbounded","unknown"], [3,5,7,1,6,2,4,8,0])
xmlwriteroutputtype = Enum("xmlwriteroutputtype", ["col","row"], [1,0])
rescode = Enum("rescode", ["err_acc_afe_domain_mismatch","err_acc_invalid_entry_index","err_acc_invalid_index","err_ad_invalid_codelist","err_afe_invalid_index","err_api_array_too_small","err_api_cb_connect","err_api_fatal_error","err_api_internal","err_appending_too_big_cone","err_arg_is_too_large","err_arg_is_too_small","err_argument_dimension","err_argument_is_too_large","err_argument_is_too_small","err_argument_lenneq","err_argument_perm_array","err_argument_type","err_axis_name_specification","err_bar_var_dim","err_basis","err_basis_factor","err_basis_singular","err_blank_name","err_cbf_duplicate_acoord","err_cbf_duplicate_bcoord","err_cbf_duplicate_con","err_cbf_duplicate_int","err_cbf_duplicate_obj","err_cbf_duplicate_objacoord","err_cbf_duplicate_pow_cones","err_cbf_duplicate_pow_star_cones","err_cbf_duplicate_psdcon","err_cbf_duplicate_psdvar","err_cbf_duplicate_var","err_cbf_invalid_con_type","err_cbf_invalid_dimension_of_cones","err_cbf_invalid_dimension_of_psdcon","err_cbf_invalid_domain_dimension","err_cbf_invalid_exp_dimension","err_cbf_invalid_int_index","err_cbf_invalid_num_psdcon","err_cbf_invalid_number_of_cones","err_cbf_invalid_power","err_cbf_invalid_power_cone_index","err_cbf_invalid_power_star_cone_index","err_cbf_invalid_psdcon_block_index","err_cbf_invalid_psdcon_index","err_cbf_invalid_psdcon_variable_index","err_cbf_invalid_psdvar_dimension","err_cbf_invalid_var_type","err_cbf_no_variables","err_cbf_no_version_specified","err_cbf_obj_sense","err_cbf_parse","err_cbf_power_cone_is_too_long","err_cbf_power_cone_mismatch","err_cbf_power_star_cone_mismatch","err_cbf_syntax","err_cbf_too_few_constraints","err_cbf_too_few_ints","err_cbf_too_few_psdvar","err_cbf_too_few_variables","err_cbf_too_many_constraints","err_cbf_too_many_ints","err_cbf_too_many_variables","err_cbf_unhandled_power_cone_type","err_cbf_unhandled_power_star_cone_type","err_cbf_unsupported","err_cbf_unsupported_change","err_con_q_not_nsd","err_con_q_not_psd","err_cone_index","err_cone_overlap","err_cone_overlap_append","err_cone_parameter","err_cone_rep_var","err_cone_size","err_cone_type","err_cone_type_str","err_data_file_ext","err_dimension_specification","err_djc_afe_domain_mismatch","err_djc_domain_termsize_mismatch","err_djc_invalid_index","err_djc_invalid_term_size","err_djc_total_num_terms_mismatch","err_djc_unsupported_domain_type","err_domain_dimension","err_domain_dimension_psd","err_domain_invalid_index","err_domain_power_invalid_alpha","err_domain_power_negative_alpha","err_domain_power_nleft","err_dup_name","err_duplicate_aij","err_duplicate_barvariable_names","err_duplicate_cone_names","err_duplicate_constraint_names","err_duplicate_djc_names","err_duplicate_domain_names","err_duplicate_fij","err_duplicate_variable_names","err_end_of_file","err_factor","err_feasrepair_cannot_relax","err_feasrepair_inconsistent_bound","err_feasrepair_solving_relaxed","err_file_license","err_file_open","err_file_read","err_file_write","err_final_solution","err_first","err_firsti","err_firstj","err_fixed_bound_values","err_flexlm","err_format_string","err_global_inv_conic_problem","err_huge_aij","err_huge_c","err_huge_fij","err_identical_tasks","err_in_argument","err_index","err_index_arr_is_too_large","err_index_arr_is_too_small","err_index_is_not_unique","err_index_is_too_large","err_index_is_too_small","err_inf_dou_index","err_inf_dou_name","err_inf_in_double_data","err_inf_int_index","err_inf_int_name","err_inf_lint_index","err_inf_lint_name","err_inf_type","err_infeas_undefined","err_infinite_bound","err_int64_to_int32_cast","err_internal","err_internal_test_failed","err_inv_aptre","err_inv_bk","err_inv_bkc","err_inv_bkx","err_inv_cone_type","err_inv_cone_type_str","err_inv_marki","err_inv_markj","err_inv_name_item","err_inv_numi","err_inv_numj","err_inv_optimizer","err_inv_problem","err_inv_qcon_subi","err_inv_qcon_subj","err_inv_qcon_subk","err_inv_qcon_val","err_inv_qobj_subi","err_inv_qobj_subj","err_inv_qobj_val","err_inv_sk","err_inv_sk_str","err_inv_skc","err_inv_skn","err_inv_skx","err_inv_var_type","err_invalid_aij","err_invalid_ampl_stub","err_invalid_b","err_invalid_barvar_name","err_invalid_cfix","err_invalid_cj","err_invalid_compression","err_invalid_con_name","err_invalid_cone_name","err_invalid_fij","err_invalid_file_format_for_affine_conic_constraints","err_invalid_file_format_for_cfix","err_invalid_file_format_for_cones","err_invalid_file_format_for_disjunctive_constraints","err_invalid_file_format_for_free_constraints","err_invalid_file_format_for_nonlinear","err_invalid_file_format_for_quadratic_terms","err_invalid_file_format_for_ranged_constraints","err_invalid_file_format_for_sym_mat","err_invalid_file_name","err_invalid_format_type","err_invalid_g","err_invalid_idx","err_invalid_iomode","err_invalid_max_num","err_invalid_name_in_sol_file","err_invalid_obj_name","err_invalid_objective_sense","err_invalid_problem_type","err_invalid_sol_file_name","err_invalid_stream","err_invalid_surplus","err_invalid_sym_mat_dim","err_invalid_task","err_invalid_utf8","err_invalid_var_name","err_invalid_wchar","err_invalid_whichsol","err_json_data","err_json_format","err_json_missing_data","err_json_number_overflow","err_json_string","err_json_syntax","err_last","err_lasti","err_lastj","err_lau_arg_k","err_lau_arg_m","err_lau_arg_n","err_lau_arg_trans","err_lau_arg_transa","err_lau_arg_transb","err_lau_arg_uplo","err_lau_invalid_lower_triangular_matrix","err_lau_invalid_sparse_symmetric_matrix","err_lau_not_positive_definite","err_lau_singular_matrix","err_lau_unknown","err_license","err_license_cannot_allocate","err_license_cannot_connect","err_license_expired","err_license_feature","err_license_invalid_hostid","err_license_max","err_license_moseklm_daemon","err_license_no_server_line","err_license_no_server_support","err_license_old_server_version","err_license_server","err_license_server_version","err_license_version","err_link_file_dll","err_living_tasks","err_lower_bound_is_a_nan","err_lp_dup_slack_name","err_lp_empty","err_lp_file_format","err_lp_free_constraint","err_lp_incompatible","err_lp_indicator_var","err_lp_invalid_con_name","err_lp_invalid_var_name","err_lp_write_conic_problem","err_lp_write_geco_problem","err_lu_max_num_tries","err_max_len_is_too_small","err_maxnumbarvar","err_maxnumcon","err_maxnumcone","err_maxnumqnz","err_maxnumvar","err_mio_internal","err_mio_invalid_node_optimizer","err_mio_invalid_root_optimizer","err_mio_no_optimizer","err_mismatching_dimension","err_missing_license_file","err_mixed_conic_and_nl","err_mps_cone_overlap","err_mps_cone_repeat","err_mps_cone_type","err_mps_duplicate_q_element","err_mps_file","err_mps_inv_field","err_mps_inv_marker","err_mps_inv_sec_order","err_mps_invalid_bound_key","err_mps_invalid_con_key","err_mps_invalid_indicator_constraint","err_mps_invalid_indicator_quadratic_constraint","err_mps_invalid_indicator_value","err_mps_invalid_indicator_variable","err_mps_invalid_key","err_mps_invalid_obj_name","err_mps_invalid_objsense","err_mps_invalid_sec_name","err_mps_mul_con_name","err_mps_mul_csec","err_mps_mul_qobj","err_mps_mul_qsec","err_mps_no_objective","err_mps_non_symmetric_q","err_mps_null_con_name","err_mps_null_var_name","err_mps_splitted_var","err_mps_tab_in_field2","err_mps_tab_in_field3","err_mps_tab_in_field5","err_mps_undef_con_name","err_mps_undef_var_name","err_mps_write_cplex_invalid_cone_type","err_mul_a_element","err_name_is_null","err_name_max_len","err_nan_in_blc","err_nan_in_blx","err_nan_in_buc","err_nan_in_bux","err_nan_in_c","err_nan_in_double_data","err_negative_append","err_negative_surplus","err_newer_dll","err_no_bars_for_solution","err_no_barx_for_solution","err_no_basis_sol","err_no_doty","err_no_dual_for_itg_sol","err_no_dual_infeas_cer","err_no_init_env","err_no_optimizer_var_type","err_no_primal_infeas_cer","err_no_snx_for_bas_sol","err_no_solution_in_callback","err_non_unique_array","err_nonconvex","err_nonlinear_equality","err_nonlinear_ranged","err_not_power_domain","err_null_env","err_null_pointer","err_null_task","err_num_arguments","err_numconlim","err_numvarlim","err_obj_q_not_nsd","err_obj_q_not_psd","err_objective_range","err_older_dll","err_opf_dual_integer_solution","err_opf_duplicate_bound","err_opf_duplicate_cone_entry","err_opf_duplicate_constraint_name","err_opf_incorrect_tag_param","err_opf_invalid_cone_type","err_opf_invalid_tag","err_opf_mismatched_tag","err_opf_premature_eof","err_opf_syntax","err_opf_too_large","err_optimizer_license","err_overflow","err_param_index","err_param_is_too_large","err_param_is_too_small","err_param_name","err_param_name_dou","err_param_name_int","err_param_name_str","err_param_type","err_param_value_str","err_platform_not_licensed","err_postsolve","err_pro_item","err_prob_license","err_ptf_format","err_ptf_incompatibility","err_ptf_inconsistency","err_ptf_undefined_item","err_qcon_subi_too_large","err_qcon_subi_too_small","err_qcon_upper_triangle","err_qobj_upper_triangle","err_read_format","err_read_lp_missing_end_tag","err_read_lp_nonexisting_name","err_remove_cone_variable","err_repair_invalid_problem","err_repair_optimization_failed","err_sen_bound_invalid_lo","err_sen_bound_invalid_up","err_sen_format","err_sen_index_invalid","err_sen_index_range","err_sen_invalid_regexp","err_sen_numerical","err_sen_solution_status","err_sen_undef_name","err_sen_unhandled_problem_type","err_server_access_token","err_server_address","err_server_certificate","err_server_connect","err_server_problem_size","err_server_protocol","err_server_status","err_server_tls_client","err_server_token","err_shape_is_too_large","err_size_license","err_size_license_con","err_size_license_intvar","err_size_license_numcores","err_size_license_var","err_slice_size","err_sol_file_invalid_number","err_solitem","err_solver_probtype","err_space","err_space_leaking","err_space_no_info","err_sparsity_specification","err_sym_mat_duplicate","err_sym_mat_huge","err_sym_mat_invalid","err_sym_mat_invalid_col_index","err_sym_mat_invalid_row_index","err_sym_mat_invalid_value","err_sym_mat_not_lower_tringular","err_task_incompatible","err_task_invalid","err_task_write","err_thread_cond_init","err_thread_create","err_thread_mutex_init","err_thread_mutex_lock","err_thread_mutex_unlock","err_toconic_constr_not_conic","err_toconic_constr_q_not_psd","err_toconic_constraint_fx","err_toconic_constraint_ra","err_toconic_objective_not_psd","err_too_small_a_truncation_value","err_too_small_max_num_nz","err_too_small_maxnumanz","err_unallowed_whichsol","err_unb_step_size","err_undef_solution","err_undefined_objective_sense","err_unhandled_solution_status","err_unknown","err_upper_bound_is_a_nan","err_upper_triangle","err_whichitem_not_allowed","err_whichsol","err_write_lp_format","err_write_lp_non_unique_name","err_write_mps_invalid_name","err_write_opf_invalid_var_name","err_writing_file","err_xml_invalid_problem_type","err_y_is_undefined","ok","trm_internal","trm_internal_stop","trm_lost_race","trm_max_iterations","trm_max_num_setbacks","trm_max_time","trm_mio_num_branches","trm_mio_num_relaxs","trm_num_max_num_int_solutions","trm_numerical_problem","trm_objective_range","trm_stall","trm_user_callback","wrn_ana_almost_int_bounds","wrn_ana_c_zero","wrn_ana_close_bounds","wrn_ana_empty_cols","wrn_ana_large_bounds","wrn_dropped_nz_qobj","wrn_duplicate_barvariable_names","wrn_duplicate_cone_names","wrn_duplicate_constraint_names","wrn_duplicate_variable_names","wrn_eliminator_space","wrn_empty_name","wrn_ignore_integer","wrn_incomplete_linear_dependency_check","wrn_invalid_mps_name","wrn_invalid_mps_obj_name","wrn_large_aij","wrn_large_bound","wrn_large_cj","wrn_large_con_fx","wrn_large_fij","wrn_large_lo_bound","wrn_large_up_bound","wrn_license_expire","wrn_license_feature_expire","wrn_license_server","wrn_lp_drop_variable","wrn_lp_old_quad_format","wrn_mio_infeasible_final","wrn_modified_double_parameter","wrn_mps_split_bou_vector","wrn_mps_split_ran_vector","wrn_mps_split_rhs_vector","wrn_name_max_len","wrn_no_dualizer","wrn_no_global_optimizer","wrn_no_infeasibility_report_when_matrix_variables","wrn_nz_in_upr_tri","wrn_open_param_file","wrn_param_ignored_cmio","wrn_param_name_dou","wrn_param_name_int","wrn_param_name_str","wrn_param_str_value","wrn_presolve_outofspace","wrn_presolve_primal_pertubations","wrn_sol_file_ignored_con","wrn_sol_file_ignored_var","wrn_sol_filter","wrn_spar_max_len","wrn_sym_mat_large","wrn_too_few_basis_vars","wrn_too_many_basis_vars","wrn_undef_sol_file_name","wrn_using_generic_names","wrn_write_changed_names","wrn_write_discarded_cfix","wrn_write_lp_duplicate_con_names","wrn_write_lp_duplicate_var_names","wrn_write_lp_invalid_con_names","wrn_write_lp_invalid_var_names","wrn_zero_aij","wrn_zeros_in_sparse_col","wrn_zeros_in_sparse_row"], [20602,20601,20600,3102,20500,3001,3002,3005,3999,1311,1227,1226,1201,5005,5004,1197,1299,1198,1083,3920,1266,1610,1615,1070,7117,7116,7108,7111,7107,7115,7130,7131,7201,7124,7110,7113,7141,7202,7114,7127,7122,7200,7140,7132,7134,7135,7205,7203,7204,7125,7112,7102,7105,7101,7100,7133,7138,7139,7106,7119,7120,7126,7118,7103,7121,7104,7136,7137,7123,7210,1294,1293,1300,1302,1307,1320,1303,1301,1305,1306,1055,1082,20702,20704,20700,20703,20705,20701,20401,20402,20400,20404,20405,20406,1071,1385,4502,4503,4500,4505,4504,20100,4501,1059,1650,1700,1702,1701,1007,1052,1053,1054,1560,1570,1285,1287,1420,1014,1072,1503,1380,1375,20102,3101,1200,1235,1222,1221,1205,1204,1203,1219,1230,1451,1220,1231,1225,1234,1232,3910,1400,3800,3000,3500,1253,1255,1256,1257,1272,1271,2501,2502,1280,2503,2504,1550,1500,1405,1406,1404,1407,1401,1402,1403,1270,1269,1267,1274,1268,1258,1473,3700,20150,1079,1469,1474,1800,1076,1078,20101,4012,4001,4005,4011,4003,4010,4006,4002,4000,1056,1283,20103,1246,1801,1247,1170,1075,1445,6000,1057,1062,1275,3950,1064,2900,1077,2901,1228,1179,1178,1180,1177,1176,1175,1571,1286,1288,7012,7010,7011,7018,7015,7016,7017,7002,7019,7001,7000,7005,1000,1020,1021,1001,1018,1025,1016,1017,1028,1027,1003,1015,1026,1002,1040,1066,1390,1152,1151,1157,1155,1150,1160,1171,1154,1163,1164,2800,1289,1242,1240,1304,1243,1241,5010,7701,7700,1551,1074,1008,1501,1118,1119,1117,1121,1100,1101,1102,1115,1108,1107,1130,1133,1132,1131,1129,1128,1122,1109,1112,1116,1114,1113,1110,1120,1103,1104,1111,1125,1126,1127,1105,1106,7750,1254,1760,1750,1461,1471,1462,1472,1470,1450,1578,1573,1036,3916,3915,1600,22010,2950,2001,1063,1552,2000,2953,2500,5000,1291,1290,1292,20403,1060,1065,1061,1199,1250,1251,1296,1295,1260,1035,1146,1138,1143,1139,1141,1140,1142,1137,1136,1134,1144,1013,1590,1210,1215,1216,1206,1207,1208,1209,1218,1217,1019,1580,1281,1006,1184,1181,1183,1182,1409,1408,1417,1415,1090,1159,1162,1310,1710,1711,3054,3053,3050,3055,3052,3056,3058,3057,3051,3080,8007,8004,8005,8000,8008,8001,8002,8006,8003,1202,1005,1010,1012,3900,1011,1572,1350,1237,1259,1051,1080,1081,1073,3944,1482,1480,3941,3940,3943,3942,2560,2561,2562,1049,1048,1045,1046,1047,7803,7800,7801,7802,7804,1421,1245,1252,1248,3100,22000,1446,6010,1050,1391,6020,1238,1236,1158,1161,1153,1156,1166,3600,1449,0,100030,100031,100027,100000,100020,100001,100009,100008,100015,100025,100002,100006,100007,904,901,903,902,900,201,852,853,850,851,801,502,250,800,504,505,62,51,57,54,980,52,53,500,509,501,85,80,270,970,72,71,70,65,950,251,930,200,50,516,510,511,512,515,802,803,351,352,300,66,960,400,405,350,503,830,831,857,855,856,854,63,710,705])
rescodetype = Enum("rescodetype", ["err","ok","trm","unk","wrn"], [3,0,2,4,1])
scalingtype = Enum("scalingtype", ["free","none"], [0,1])
scalingmethod = Enum("scalingmethod", ["free","pow2"], [1,0])
sensitivitytype = Enum("sensitivitytype", ["basis"], [0])
simseltype = Enum("simseltype", ["ase","devex","free","full","partial","se"], [2,3,0,1,5,4])
solitem = Enum("solitem", ["slc","slx","snx","suc","sux","xc","xx","y"], [3,5,7,4,6,0,1,2])
solsta = Enum("solsta", ["dual_feas","dual_illposed_cer","dual_infeas_cer","integer_optimal","optimal","prim_and_dual_feas","prim_feas","prim_illposed_cer","prim_infeas_cer","unknown"], [3,8,6,9,1,4,2,7,5,0])
soltype = Enum("soltype", ["bas","itg","itr"], [1,2,0])
solveform = Enum("solveform", ["dual","free","primal"], [2,0,1])
sparam = Enum("sparam", ["bas_sol_file_name","data_file_name","debug_file_name","int_sol_file_name","itr_sol_file_name","mio_debug_string","param_comment_sign","param_read_file_name","param_write_file_name","read_mps_bou_name","read_mps_obj_name","read_mps_ran_name","read_mps_rhs_name","remote_optserver_host","remote_tls_cert","remote_tls_cert_path","sensitivity_file_name","sensitivity_res_file_name","sol_filter_xc_low","sol_filter_xc_upr","sol_filter_xx_low","sol_filter_xx_upr","stat_key","stat_name","write_lp_gen_var_name"], [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
stakey = Enum("stakey", ["bas","fix","inf","low","supbas","unk","upr"], [1,5,6,3,2,0,4])
startpointtype = Enum("startpointtype", ["constant","free","guess","satisfy_bounds"], [2,0,1,3])
streamtype = Enum("streamtype", ["err","log","msg","wrn"], [2,0,1,3])
value = Enum("value", ["license_buffer_length","max_str_len"], [21,1024])
variabletype = Enum("variabletype", ["type_cont","type_int"], [0,1])




class Env:
    def __init__(self,licensefile=None,debugfile=None,globalenv=False):
        args = {}
        if debugfile is not None: args["dbgfile"] = debugfile
        if globalenv: args["globalenv"] = globalenv
        self.__obj = _msk.Env(**args)

        if licensefile is not None:
            if isinstance(licensefile,str):
                res,_ = self.__obj.putlicensepath_s_2(licensefile)
                if res != 0:
                    self.__del__()
                    raise Error(rescode(res),"Error %d" % res)
        if not globalenv:
            self.__obj.enablegarcolenv()

    def __getlasterror(self,res):
        return rescode(res),""

    def set_Stream(self,whichstream,func):
        if isinstance(whichstream, streamtype):
            if func is None:
                self.__obj.remove_Stream(whichstream)
            else:
                self.__obj.set_Stream(whichstream,func)
        else:
            raise TypeError("Invalid stream %s" % whichstream)

    def __del__(self):
        try:
            o = self.__obj
            del self.__obj
        except AttributeError:
            pass
        else:
            o.dispose()

    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        self.__del__()

    def Task(self,numcon=0,numvar=0):
        return Task(self,numcon,numvar)

    def __optimizebatch_idiOOO_7(self,israce,maxtime,numthreads,task,trmcode,rcode):
      if task is None:
        raise TypeError("Argument task may not be None")
      if task is not None:
        if not all([ isinstance(__tmp_1540,Task) for __tmp_1540 in task]):
          raise TypeError("Expected a list of Task for argument task")
      if trmcode is None:
        trmcode_ = None
      else:
        # o
        _tmparray_trmcode_ = array.array("i",[0 for _ in range(len(trmcode))])
        trmcode_ = memoryview(_tmparray_trmcode_)
      if rcode is None:
        rcode_ = None
      else:
        # o
        _tmparray_rcode_ = array.array("i",[0 for _ in range(len(rcode))])
        rcode_ = memoryview(_tmparray_rcode_)
      _res_optimizebatch,_retargs_optimizebatch = self.__obj.optimizebatch_idiOOO_7(israce,maxtime,numthreads,[ __tmp_1541._Task__obj for __tmp_1541 in task ],trmcode_,rcode_)
      if _res_optimizebatch != 0:
        _,_msg_optimizebatch = self.__getlasterror(_res_optimizebatch)
        raise Error(rescode(_res_optimizebatch),_msg_optimizebatch)
      for __tmp_1544 in range(len(trmcode)): trmcode[__tmp_1544] = rescode(trmcode_[__tmp_1544])
      for __tmp_1545 in range(len(rcode)): rcode[__tmp_1545] = rescode(rcode_[__tmp_1545])
    def __optimizebatch_idiOOO_5(self,israce,maxtime,numthreads,task):
      if task is None:
        raise TypeError("Argument task may not be None")
      if task is not None:
        if not all([ isinstance(__tmp_1546,Task) for __tmp_1546 in task]):
          raise TypeError("Expected a list of Task for argument task")
      trmcode_ = bytearray(0)
      rcode_ = bytearray(0)
      _res_optimizebatch,_retargs_optimizebatch = self.__obj.optimizebatch_idiOOO_5(israce,maxtime,numthreads,[ __tmp_1547._Task__obj for __tmp_1547 in task ],trmcode_,rcode_)
      if _res_optimizebatch != 0:
        _,_msg_optimizebatch = self.__getlasterror(_res_optimizebatch)
        raise Error(rescode(_res_optimizebatch),_msg_optimizebatch)
      trmcode_ints = array.array("i")
      trmcode_ints.frombytes(trmcode_)
      trmcode = [ rescode(__tmp_1550) for __tmp_1550 in trmcode_ints ]
      rcode_ints = array.array("i")
      rcode_ints.frombytes(rcode_)
      rcode = [ rescode(__tmp_1551) for __tmp_1551 in rcode_ints ]
      return (trmcode,rcode)
    def optimizebatch(self,*args,**kwds):
      """
      Optimize a number of tasks in parallel using a specified number of threads.
    
      optimizebatch(israce,
                    maxtime,
                    numthreads,
                    task,
                    trmcode,
                    rcode)
      optimizebatch(israce,maxtime,numthreads,task) -> (trmcode,rcode)
        [israce : bool]  If nonzero, then the function is terminated after the first task has been completed.  
        [maxtime : float64]  Time limit for the function.  
        [numthreads : int32]  Number of threads to be employed.  
        [rcode : array(mosek.rescode)]  The response code for each task.  
        [task : array(Task)]  An array of tasks to optimize in parallel.  
        [trmcode : array(mosek.rescode)]  The termination code for each task.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 7: return self.__optimizebatch_idiOOO_7(*args,**kwds)
      elif len(args)+len(kwds)+1 == 5: return self.__optimizebatch_idiOOO_5(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __checkoutlicense_i_2(self,feature):
      _res_checkoutlicense,_retargs_checkoutlicense = self.__obj.checkoutlicense_i_2(feature)
      if _res_checkoutlicense != 0:
        _,_msg_checkoutlicense = self.__getlasterror(_res_checkoutlicense)
        raise Error(rescode(_res_checkoutlicense),_msg_checkoutlicense)
    def checkoutlicense(self,*args,**kwds):
      """
      Check out a license feature from the license server ahead of time.
    
      checkoutlicense(feature)
        [feature : mosek.feature]  Feature to check out from the license system.  
      """
      return self.__checkoutlicense_i_2(*args,**kwds)
    def __checkinlicense_i_2(self,feature):
      _res_checkinlicense,_retargs_checkinlicense = self.__obj.checkinlicense_i_2(feature)
      if _res_checkinlicense != 0:
        _,_msg_checkinlicense = self.__getlasterror(_res_checkinlicense)
        raise Error(rescode(_res_checkinlicense),_msg_checkinlicense)
    def checkinlicense(self,*args,**kwds):
      """
      Check in a license feature back to the license server ahead of time.
    
      checkinlicense(feature)
        [feature : mosek.feature]  Feature to check in to the license system.  
      """
      return self.__checkinlicense_i_2(*args,**kwds)
    def __checkinall__1(self):
      _res_checkinall,_retargs_checkinall = self.__obj.checkinall__1()
      if _res_checkinall != 0:
        _,_msg_checkinall = self.__getlasterror(_res_checkinall)
        raise Error(rescode(_res_checkinall),_msg_checkinall)
    def checkinall(self,*args,**kwds):
      """
      Check in all unused license features to the license token server.
    
      checkinall()
      """
      return self.__checkinall__1(*args,**kwds)
    def __expirylicenses__1(self):
      _res_expirylicenses,_retargs_expirylicenses = self.__obj.expirylicenses__1()
      if _res_expirylicenses != 0:
        _,_msg_expirylicenses = self.__getlasterror(_res_expirylicenses)
        raise Error(rescode(_res_expirylicenses),_msg_expirylicenses)
      else:
        (expiry) = _retargs_expirylicenses
      return (expiry)
    def expirylicenses(self,*args,**kwds):
      """
      Reports when the first license feature expires.
    
      expirylicenses() -> (expiry)
        [expiry : int64]  If nonnegative, then it is the minimum number days to expiry of any feature that has been checked out.  
      """
      return self.__expirylicenses__1(*args,**kwds)
    def __resetexpirylicenses__1(self):
      _res_resetexpirylicenses,_retargs_resetexpirylicenses = self.__obj.resetexpirylicenses__1()
      if _res_resetexpirylicenses != 0:
        _,_msg_resetexpirylicenses = self.__getlasterror(_res_resetexpirylicenses)
        raise Error(rescode(_res_resetexpirylicenses),_msg_resetexpirylicenses)
    def resetexpirylicenses(self,*args,**kwds):
      """
      Reset the license expiry reporting startpoint.
    
      resetexpirylicenses()
      """
      return self.__resetexpirylicenses__1(*args,**kwds)
    def __echointro_i_2(self,longver):
      _res_echointro,_retargs_echointro = self.__obj.echointro_i_2(longver)
      if _res_echointro != 0:
        _,_msg_echointro = self.__getlasterror(_res_echointro)
        raise Error(rescode(_res_echointro),_msg_echointro)
    def echointro(self,*args,**kwds):
      """
      Prints an intro to message stream.
    
      echointro(longver)
        [longver : int32]  If non-zero, then the intro is slightly longer.  
      """
      return self.__echointro_i_2(*args,**kwds)
    @staticmethod
    def __getcodedesc_iOO_1(code):
      symname = bytearray(0)
      str = bytearray(0)
      _res_getcodedesc,_retargs_getcodedesc = _msk.Env.getcodedesc_iOO_1(code,symname,str)
      if _res_getcodedesc != 0:
        raise Error(rescode(_res_getcodedesc),"")
      __tmp_1552 = symname.find(b"\0")
      if __tmp_1552 >= 0:
        symname = symname[:__tmp_1552]
      __tmp_1553 = str.find(b"\0")
      if __tmp_1553 >= 0:
        str = str[:__tmp_1553]
      return (symname.decode("utf-8",errors="ignore"),str.decode("utf-8",errors="ignore"))
    @staticmethod
    def getcodedesc(*args,**kwds):
      """
      Obtains a short description of a response code.
    
      getcodedesc(code) -> (symname,str)
        [code : mosek.rescode]  A valid response code.  
        [str : str]  Obtains a short description of a response code.  
        [symname : str]  Symbolic name corresponding to the code.  
      """
      return Env.__getcodedesc_iOO_1(*args,**kwds)
    @staticmethod
    def __getversion__0():
      _res_getversion,_retargs_getversion = _msk.Env.getversion__0()
      if _res_getversion != 0:
        raise Error(rescode(_res_getversion),"")
      else:
        (major,minor,revision) = _retargs_getversion
      return (major,minor,revision)
    @staticmethod
    def getversion(*args,**kwds):
      """
      Obtains MOSEK version information.
    
      getversion() -> (major,minor,revision)
        [major : int32]  Major version number.  
        [minor : int32]  Minor version number.  
        [revision : int32]  Revision number.  
      """
      return Env.__getversion__0(*args,**kwds)
    def __linkfiletoenvstream_isi_4(self,whichstream,filename,append):
      _res_linkfiletoenvstream,_retargs_linkfiletoenvstream = self.__obj.linkfiletoenvstream_isi_4(whichstream,filename,append)
      if _res_linkfiletoenvstream != 0:
        _,_msg_linkfiletoenvstream = self.__getlasterror(_res_linkfiletoenvstream)
        raise Error(rescode(_res_linkfiletoenvstream),_msg_linkfiletoenvstream)
    def linkfiletostream(self,*args,**kwds):
      """
      Directs all output from a stream to a file.
    
      linkfiletostream(whichstream,filename,append)
        [append : int32]  If this argument is 0 the file will be overwritten, otherwise it will be appended to.  
        [filename : str]  A valid file name.  
        [whichstream : mosek.streamtype]  Index of the stream.  
      """
      return self.__linkfiletoenvstream_isi_4(*args,**kwds)
    def __putlicensedebug_i_2(self,licdebug):
      _res_putlicensedebug,_retargs_putlicensedebug = self.__obj.putlicensedebug_i_2(licdebug)
      if _res_putlicensedebug != 0:
        _,_msg_putlicensedebug = self.__getlasterror(_res_putlicensedebug)
        raise Error(rescode(_res_putlicensedebug),_msg_putlicensedebug)
    def putlicensedebug(self,*args,**kwds):
      """
      Enables debug information for the license system.
    
      putlicensedebug(licdebug)
        [licdebug : int32]  Enable output of license check-out debug information.  
      """
      return self.__putlicensedebug_i_2(*args,**kwds)
    def __putlicensecode_O_2(self,code):
      copyback_code = False
      if code is None:
        code_ = None
        memview_code = None
      else:
        try:
          memview_code = memoryview(code)
        except TypeError:
          try:
            _tmparray_code = array.array("i",code)
          except TypeError:
            raise TypeError("Argument code has wrong type") from None
          else:
            memview_code = memoryview(_tmparray_code)
            copyback_code = True
            code_ = _tmparray_code
        else:
          if memview_code.ndim != 1:
            raise TypeError("Argument code must be one-dimensional")
          if memview_code.format != "i":
            _tmparray_code = array.array("i",code)
            memview_code = memoryview(_tmparray_code)
            copyback_code = True
            code_ = _tmparray_code
      _res_putlicensecode,_retargs_putlicensecode = self.__obj.putlicensecode_O_2(memview_code)
      if _res_putlicensecode != 0:
        _,_msg_putlicensecode = self.__getlasterror(_res_putlicensecode)
        raise Error(rescode(_res_putlicensecode),_msg_putlicensecode)
    def putlicensecode(self,*args,**kwds):
      """
      Input a runtime license code.
    
      putlicensecode(code)
        [code : array(int32)]  A license key string.  
      """
      return self.__putlicensecode_O_2(*args,**kwds)
    def __putlicensewait_i_2(self,licwait):
      _res_putlicensewait,_retargs_putlicensewait = self.__obj.putlicensewait_i_2(licwait)
      if _res_putlicensewait != 0:
        _,_msg_putlicensewait = self.__getlasterror(_res_putlicensewait)
        raise Error(rescode(_res_putlicensewait),_msg_putlicensewait)
    def putlicensewait(self,*args,**kwds):
      """
      Control whether mosek should wait for an available license if no license is available.
    
      putlicensewait(licwait)
        [licwait : int32]  Enable waiting for a license.  
      """
      return self.__putlicensewait_i_2(*args,**kwds)
    def __putlicensepath_s_2(self,licensepath):
      _res_putlicensepath,_retargs_putlicensepath = self.__obj.putlicensepath_s_2(licensepath)
      if _res_putlicensepath != 0:
        _,_msg_putlicensepath = self.__getlasterror(_res_putlicensepath)
        raise Error(rescode(_res_putlicensepath),_msg_putlicensepath)
    def putlicensepath(self,*args,**kwds):
      """
      Set the path to the license file.
    
      putlicensepath(licensepath)
        [licensepath : str]  A path specifying where to search for the license.  
      """
      return self.__putlicensepath_s_2(*args,**kwds)
    def __axpy_idOO_5(self,n,alpha,x,y):
      if x is None:
        raise TypeError("Argument x may not be None")
      copyback_x = False
      if x is None:
        x_ = None
        memview_x = None
      else:
        try:
          memview_x = memoryview(x)
        except TypeError:
          try:
            _tmparray_x = array.array("d",x)
          except TypeError:
            raise TypeError("Argument x has wrong type") from None
          else:
            memview_x = memoryview(_tmparray_x)
            copyback_x = True
            x_ = _tmparray_x
        else:
          if memview_x.ndim != 1:
            raise TypeError("Argument x must be one-dimensional")
          if memview_x.format != "d":
            _tmparray_x = array.array("d",x)
            memview_x = memoryview(_tmparray_x)
            copyback_x = True
            x_ = _tmparray_x
      if y is None:
        raise TypeError("Argument y may not be None")
      copyback_y = False
      if y is None:
        y_ = None
        memview_y = None
      else:
        try:
          memview_y = memoryview(y)
        except TypeError:
          try:
            _tmparray_y = array.array("d",y)
          except TypeError:
            raise TypeError("Argument y has wrong type") from None
          else:
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
        else:
          if memview_y.ndim != 1:
            raise TypeError("Argument y must be one-dimensional")
          if memview_y.format != "d":
            _tmparray_y = array.array("d",y)
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
      _res_axpy,_retargs_axpy = self.__obj.axpy_idOO_5(n,alpha,memview_x,memview_y)
      if _res_axpy != 0:
        _,_msg_axpy = self.__getlasterror(_res_axpy)
        raise Error(rescode(_res_axpy),_msg_axpy)
      if copyback_y:
        for __tmp_1559 in range(len(y)): y[__tmp_1559] = y_[__tmp_1559]
    def axpy(self,*args,**kwds):
      """
      Computes vector addition and multiplication by a scalar.
    
      axpy(n,alpha,x,y)
        [alpha : float64]  The scalar that multiplies x.  
        [n : int32]  Length of the vectors.  
        [x : array(float64)]  The x vector.  
        [y : array(float64)]  The y vector.  
      """
      return self.__axpy_idOO_5(*args,**kwds)
    def __dot_iOO_4(self,n,x,y):
      if x is None:
        raise TypeError("Argument x may not be None")
      copyback_x = False
      if x is None:
        x_ = None
        memview_x = None
      else:
        try:
          memview_x = memoryview(x)
        except TypeError:
          try:
            _tmparray_x = array.array("d",x)
          except TypeError:
            raise TypeError("Argument x has wrong type") from None
          else:
            memview_x = memoryview(_tmparray_x)
            copyback_x = True
            x_ = _tmparray_x
        else:
          if memview_x.ndim != 1:
            raise TypeError("Argument x must be one-dimensional")
          if memview_x.format != "d":
            _tmparray_x = array.array("d",x)
            memview_x = memoryview(_tmparray_x)
            copyback_x = True
            x_ = _tmparray_x
      if y is None:
        raise TypeError("Argument y may not be None")
      copyback_y = False
      if y is None:
        y_ = None
        memview_y = None
      else:
        try:
          memview_y = memoryview(y)
        except TypeError:
          try:
            _tmparray_y = array.array("d",y)
          except TypeError:
            raise TypeError("Argument y has wrong type") from None
          else:
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
        else:
          if memview_y.ndim != 1:
            raise TypeError("Argument y must be one-dimensional")
          if memview_y.format != "d":
            _tmparray_y = array.array("d",y)
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
      _res_dot,_retargs_dot = self.__obj.dot_iOO_4(n,memview_x,memview_y)
      if _res_dot != 0:
        _,_msg_dot = self.__getlasterror(_res_dot)
        raise Error(rescode(_res_dot),_msg_dot)
      else:
        (xty) = _retargs_dot
      return (xty)
    def dot(self,*args,**kwds):
      """
      Computes the inner product of two vectors.
    
      dot(n,x,y) -> (xty)
        [n : int32]  Length of the vectors.  
        [x : array(float64)]  The x vector.  
        [xty : float64]  The result of the inner product.  
        [y : array(float64)]  The y vector.  
      """
      return self.__dot_iOO_4(*args,**kwds)
    def __gemv_iiidOOdO_9(self,transa,m,n,alpha,a,x,beta,y):
      if a is None:
        raise TypeError("Argument a may not be None")
      copyback_a = False
      if a is None:
        a_ = None
        memview_a = None
      else:
        try:
          memview_a = memoryview(a)
        except TypeError:
          try:
            _tmparray_a = array.array("d",a)
          except TypeError:
            raise TypeError("Argument a has wrong type") from None
          else:
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
        else:
          if memview_a.ndim != 1:
            raise TypeError("Argument a must be one-dimensional")
          if memview_a.format != "d":
            _tmparray_a = array.array("d",a)
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
      if x is None:
        raise TypeError("Argument x may not be None")
      copyback_x = False
      if x is None:
        x_ = None
        memview_x = None
      else:
        try:
          memview_x = memoryview(x)
        except TypeError:
          try:
            _tmparray_x = array.array("d",x)
          except TypeError:
            raise TypeError("Argument x has wrong type") from None
          else:
            memview_x = memoryview(_tmparray_x)
            copyback_x = True
            x_ = _tmparray_x
        else:
          if memview_x.ndim != 1:
            raise TypeError("Argument x must be one-dimensional")
          if memview_x.format != "d":
            _tmparray_x = array.array("d",x)
            memview_x = memoryview(_tmparray_x)
            copyback_x = True
            x_ = _tmparray_x
      if y is None:
        raise TypeError("Argument y may not be None")
      copyback_y = False
      if y is None:
        y_ = None
        memview_y = None
      else:
        try:
          memview_y = memoryview(y)
        except TypeError:
          try:
            _tmparray_y = array.array("d",y)
          except TypeError:
            raise TypeError("Argument y has wrong type") from None
          else:
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
        else:
          if memview_y.ndim != 1:
            raise TypeError("Argument y must be one-dimensional")
          if memview_y.format != "d":
            _tmparray_y = array.array("d",y)
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
      _res_gemv,_retargs_gemv = self.__obj.gemv_iiidOOdO_9(transa,m,n,alpha,memview_a,memview_x,beta,memview_y)
      if _res_gemv != 0:
        _,_msg_gemv = self.__getlasterror(_res_gemv)
        raise Error(rescode(_res_gemv),_msg_gemv)
      if copyback_y:
        for __tmp_1568 in range(len(y)): y[__tmp_1568] = y_[__tmp_1568]
    def gemv(self,*args,**kwds):
      """
      Computes dense matrix times a dense vector product.
    
      gemv(transa,m,n,alpha,a,x,beta,y)
        [a : array(float64)]  A pointer to the array storing matrix A in a column-major format.  
        [alpha : float64]  A scalar value multiplying the matrix A.  
        [beta : float64]  A scalar value multiplying the vector y.  
        [m : int32]  Specifies the number of rows of the matrix A.  
        [n : int32]  Specifies the number of columns of the matrix A.  
        [transa : mosek.transpose]  Indicates whether the matrix A must be transposed.  
        [x : array(float64)]  A pointer to the array storing the vector x.  
        [y : array(float64)]  A pointer to the array storing the vector y.  
      """
      return self.__gemv_iiidOOdO_9(*args,**kwds)
    def __gemm_iiiiidOOdO_11(self,transa,transb,m,n,k,alpha,a,b,beta,c):
      if a is None:
        raise TypeError("Argument a may not be None")
      copyback_a = False
      if a is None:
        a_ = None
        memview_a = None
      else:
        try:
          memview_a = memoryview(a)
        except TypeError:
          try:
            _tmparray_a = array.array("d",a)
          except TypeError:
            raise TypeError("Argument a has wrong type") from None
          else:
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
        else:
          if memview_a.ndim != 1:
            raise TypeError("Argument a must be one-dimensional")
          if memview_a.format != "d":
            _tmparray_a = array.array("d",a)
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
      if b is None:
        raise TypeError("Argument b may not be None")
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",b)
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      if c is None:
        raise TypeError("Argument c may not be None")
      copyback_c = False
      if c is None:
        c_ = None
        memview_c = None
      else:
        try:
          memview_c = memoryview(c)
        except TypeError:
          try:
            _tmparray_c = array.array("d",c)
          except TypeError:
            raise TypeError("Argument c has wrong type") from None
          else:
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
        else:
          if memview_c.ndim != 1:
            raise TypeError("Argument c must be one-dimensional")
          if memview_c.format != "d":
            _tmparray_c = array.array("d",c)
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
      _res_gemm,_retargs_gemm = self.__obj.gemm_iiiiidOOdO_11(transa,transb,m,n,k,alpha,memview_a,memview_b,beta,memview_c)
      if _res_gemm != 0:
        _,_msg_gemm = self.__getlasterror(_res_gemm)
        raise Error(rescode(_res_gemm),_msg_gemm)
      if copyback_c:
        for __tmp_1574 in range(len(c)): c[__tmp_1574] = c_[__tmp_1574]
    def gemm(self,*args,**kwds):
      """
      Performs a dense matrix multiplication.
    
      gemm(transa,transb,m,n,k,alpha,a,b,beta,c)
        [a : array(float64)]  The pointer to the array storing matrix A in a column-major format.  
        [alpha : float64]  A scalar value multiplying the result of the matrix multiplication.  
        [b : array(float64)]  The pointer to the array storing matrix B in a column-major format.  
        [beta : float64]  A scalar value that multiplies C.  
        [c : array(float64)]  The pointer to the array storing matrix C in a column-major format.  
        [k : int32]  Specifies the common dimension along which op(A) and op(B) are multiplied.  
        [m : int32]  Indicates the number of rows of matrix C.  
        [n : int32]  Indicates the number of columns of matrix C.  
        [transa : mosek.transpose]  Indicates whether the matrix A must be transposed.  
        [transb : mosek.transpose]  Indicates whether the matrix B must be transposed.  
      """
      return self.__gemm_iiiiidOOdO_11(*args,**kwds)
    def __syrk_iiiidOdO_9(self,uplo,trans,n,k,alpha,a,beta,c):
      if a is None:
        raise TypeError("Argument a may not be None")
      copyback_a = False
      if a is None:
        a_ = None
        memview_a = None
      else:
        try:
          memview_a = memoryview(a)
        except TypeError:
          try:
            _tmparray_a = array.array("d",a)
          except TypeError:
            raise TypeError("Argument a has wrong type") from None
          else:
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
        else:
          if memview_a.ndim != 1:
            raise TypeError("Argument a must be one-dimensional")
          if memview_a.format != "d":
            _tmparray_a = array.array("d",a)
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
      if c is None:
        raise TypeError("Argument c may not be None")
      copyback_c = False
      if c is None:
        c_ = None
        memview_c = None
      else:
        try:
          memview_c = memoryview(c)
        except TypeError:
          try:
            _tmparray_c = array.array("d",c)
          except TypeError:
            raise TypeError("Argument c has wrong type") from None
          else:
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
        else:
          if memview_c.ndim != 1:
            raise TypeError("Argument c must be one-dimensional")
          if memview_c.format != "d":
            _tmparray_c = array.array("d",c)
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
      _res_syrk,_retargs_syrk = self.__obj.syrk_iiiidOdO_9(uplo,trans,n,k,alpha,memview_a,beta,memview_c)
      if _res_syrk != 0:
        _,_msg_syrk = self.__getlasterror(_res_syrk)
        raise Error(rescode(_res_syrk),_msg_syrk)
      if copyback_c:
        for __tmp_1579 in range(len(c)): c[__tmp_1579] = c_[__tmp_1579]
    def syrk(self,*args,**kwds):
      """
      Performs a rank-k update of a symmetric matrix.
    
      syrk(uplo,trans,n,k,alpha,a,beta,c)
        [a : array(float64)]  The pointer to the array storing matrix A in a column-major format.  
        [alpha : float64]  A scalar value multiplying the result of the matrix multiplication.  
        [beta : float64]  A scalar value that multiplies C.  
        [c : array(float64)]  The pointer to the array storing matrix C in a column-major format.  
        [k : int32]  Indicates the number of rows or columns of A, and its rank.  
        [n : int32]  Specifies the order of C.  
        [trans : mosek.transpose]  Indicates whether the matrix A must be transposed.  
        [uplo : mosek.uplo]  Indicates whether the upper or lower triangular part of C is used.  
      """
      return self.__syrk_iiiidOdO_9(*args,**kwds)
    def __computesparsecholesky_iidOOOOOOOOOO_8(self,numthreads,ordermethod,tolsingular,anzc,aptrc,asubc,avalc):
      if anzc is None:
        raise TypeError("Argument anzc may not be None")
      copyback_anzc = False
      if anzc is None:
        anzc_ = None
        memview_anzc = None
      else:
        try:
          memview_anzc = memoryview(anzc)
        except TypeError:
          try:
            _tmparray_anzc = array.array("i",anzc)
          except TypeError:
            raise TypeError("Argument anzc has wrong type") from None
          else:
            memview_anzc = memoryview(_tmparray_anzc)
            copyback_anzc = True
            anzc_ = _tmparray_anzc
        else:
          if memview_anzc.ndim != 1:
            raise TypeError("Argument anzc must be one-dimensional")
          if memview_anzc.format != "i":
            _tmparray_anzc = array.array("i",anzc)
            memview_anzc = memoryview(_tmparray_anzc)
            copyback_anzc = True
            anzc_ = _tmparray_anzc
      if aptrc is None:
        raise TypeError("Argument aptrc may not be None")
      copyback_aptrc = False
      if aptrc is None:
        aptrc_ = None
        memview_aptrc = None
      else:
        try:
          memview_aptrc = memoryview(aptrc)
        except TypeError:
          try:
            _tmparray_aptrc = array.array("q",aptrc)
          except TypeError:
            raise TypeError("Argument aptrc has wrong type") from None
          else:
            memview_aptrc = memoryview(_tmparray_aptrc)
            copyback_aptrc = True
            aptrc_ = _tmparray_aptrc
        else:
          if memview_aptrc.ndim != 1:
            raise TypeError("Argument aptrc must be one-dimensional")
          if memview_aptrc.format != "q":
            _tmparray_aptrc = array.array("q",aptrc)
            memview_aptrc = memoryview(_tmparray_aptrc)
            copyback_aptrc = True
            aptrc_ = _tmparray_aptrc
      if asubc is None:
        raise TypeError("Argument asubc may not be None")
      copyback_asubc = False
      if asubc is None:
        asubc_ = None
        memview_asubc = None
      else:
        try:
          memview_asubc = memoryview(asubc)
        except TypeError:
          try:
            _tmparray_asubc = array.array("i",asubc)
          except TypeError:
            raise TypeError("Argument asubc has wrong type") from None
          else:
            memview_asubc = memoryview(_tmparray_asubc)
            copyback_asubc = True
            asubc_ = _tmparray_asubc
        else:
          if memview_asubc.ndim != 1:
            raise TypeError("Argument asubc must be one-dimensional")
          if memview_asubc.format != "i":
            _tmparray_asubc = array.array("i",asubc)
            memview_asubc = memoryview(_tmparray_asubc)
            copyback_asubc = True
            asubc_ = _tmparray_asubc
      if avalc is None:
        raise TypeError("Argument avalc may not be None")
      copyback_avalc = False
      if avalc is None:
        avalc_ = None
        memview_avalc = None
      else:
        try:
          memview_avalc = memoryview(avalc)
        except TypeError:
          try:
            _tmparray_avalc = array.array("d",avalc)
          except TypeError:
            raise TypeError("Argument avalc has wrong type") from None
          else:
            memview_avalc = memoryview(_tmparray_avalc)
            copyback_avalc = True
            avalc_ = _tmparray_avalc
        else:
          if memview_avalc.ndim != 1:
            raise TypeError("Argument avalc must be one-dimensional")
          if memview_avalc.format != "d":
            _tmparray_avalc = array.array("d",avalc)
            memview_avalc = memoryview(_tmparray_avalc)
            copyback_avalc = True
            avalc_ = _tmparray_avalc
      bytearray_perm = bytearray(0)
      bytearray_diag = bytearray(0)
      bytearray_lnzc = bytearray(0)
      bytearray_lptrc = bytearray(0)
      bytearray_lsubc = bytearray(0)
      bytearray_lvalc = bytearray(0)
      _res_computesparsecholesky,_retargs_computesparsecholesky = self.__obj.computesparsecholesky_iidOOOOOOOOOO_8(numthreads,ordermethod,tolsingular,memview_anzc,memview_aptrc,memview_asubc,memview_avalc,bytearray_perm,bytearray_diag,bytearray_lnzc,bytearray_lptrc,bytearray_lsubc,bytearray_lvalc)
      if _res_computesparsecholesky != 0:
        _,_msg_computesparsecholesky = self.__getlasterror(_res_computesparsecholesky)
        raise Error(rescode(_res_computesparsecholesky),_msg_computesparsecholesky)
      else:
        (lensubnval) = _retargs_computesparsecholesky
      perm = array.array("i")
      perm.frombytes(bytearray_perm)
      diag = array.array("d")
      diag.frombytes(bytearray_diag)
      lnzc = array.array("i")
      lnzc.frombytes(bytearray_lnzc)
      lptrc = array.array("q")
      lptrc.frombytes(bytearray_lptrc)
      lsubc = array.array("i")
      lsubc.frombytes(bytearray_lsubc)
      lvalc = array.array("d")
      lvalc.frombytes(bytearray_lvalc)
      return (perm,diag,lnzc,lptrc,lensubnval,lsubc,lvalc)
    def computesparsecholesky(self,*args,**kwds):
      """
      Computes a Cholesky factorization of sparse matrix.
    
      computesparsecholesky(numthreads,
                            ordermethod,
                            tolsingular,
                            anzc,
                            aptrc,
                            asubc,
                            avalc) -> 
                           (perm,
                            diag,
                            lnzc,
                            lptrc,
                            lensubnval,
                            lsubc,
                            lvalc)
        [anzc : array(int32)]  anzc[j] is the number of nonzeros in the jth column of A.  
        [aptrc : array(int64)]  aptrc[j] is a pointer to the first element in column j.  
        [asubc : array(int32)]  Row indexes for each column stored in increasing order.  
        [avalc : array(float64)]  The value corresponding to row indexed stored in asubc.  
        [diag : array(float64)]  The diagonal elements of matrix D.  
        [lensubnval : int64]  Number of elements in lsubc and lvalc.  
        [lnzc : array(int32)]  lnzc[j] is the number of non zero elements in column j.  
        [lptrc : array(int64)]  lptrc[j] is a pointer to the first row index and value in column j.  
        [lsubc : array(int32)]  Row indexes for each column stored in increasing order.  
        [lvalc : array(float64)]  The values corresponding to row indexed stored in lsubc.  
        [numthreads : int32]  The number threads that can be used to do the computation. 0 means the code makes the choice.  
        [ordermethod : int32]  If nonzero, then a sparsity preserving ordering will be employed.  
        [perm : array(int32)]  Permutation array used to specify the permutation matrix P computed by the function.  
        [tolsingular : float64]  A positive parameter controlling when a pivot is declared zero.  
      """
      return self.__computesparsecholesky_iidOOOOOOOOOO_8(*args,**kwds)
    def __sparsetriangularsolvedense_iOOOOO_7(self,transposed,lnzc,lptrc,lsubc,lvalc,b):
      if lnzc is None:
        raise TypeError("Argument lnzc may not be None")
      copyback_lnzc = False
      if lnzc is None:
        lnzc_ = None
        memview_lnzc = None
      else:
        try:
          memview_lnzc = memoryview(lnzc)
        except TypeError:
          try:
            _tmparray_lnzc = array.array("i",lnzc)
          except TypeError:
            raise TypeError("Argument lnzc has wrong type") from None
          else:
            memview_lnzc = memoryview(_tmparray_lnzc)
            copyback_lnzc = True
            lnzc_ = _tmparray_lnzc
        else:
          if memview_lnzc.ndim != 1:
            raise TypeError("Argument lnzc must be one-dimensional")
          if memview_lnzc.format != "i":
            _tmparray_lnzc = array.array("i",lnzc)
            memview_lnzc = memoryview(_tmparray_lnzc)
            copyback_lnzc = True
            lnzc_ = _tmparray_lnzc
      if lptrc is None:
        raise TypeError("Argument lptrc may not be None")
      copyback_lptrc = False
      if lptrc is None:
        lptrc_ = None
        memview_lptrc = None
      else:
        try:
          memview_lptrc = memoryview(lptrc)
        except TypeError:
          try:
            _tmparray_lptrc = array.array("q",lptrc)
          except TypeError:
            raise TypeError("Argument lptrc has wrong type") from None
          else:
            memview_lptrc = memoryview(_tmparray_lptrc)
            copyback_lptrc = True
            lptrc_ = _tmparray_lptrc
        else:
          if memview_lptrc.ndim != 1:
            raise TypeError("Argument lptrc must be one-dimensional")
          if memview_lptrc.format != "q":
            _tmparray_lptrc = array.array("q",lptrc)
            memview_lptrc = memoryview(_tmparray_lptrc)
            copyback_lptrc = True
            lptrc_ = _tmparray_lptrc
      if lsubc is None:
        raise TypeError("Argument lsubc may not be None")
      copyback_lsubc = False
      if lsubc is None:
        lsubc_ = None
        memview_lsubc = None
      else:
        try:
          memview_lsubc = memoryview(lsubc)
        except TypeError:
          try:
            _tmparray_lsubc = array.array("i",lsubc)
          except TypeError:
            raise TypeError("Argument lsubc has wrong type") from None
          else:
            memview_lsubc = memoryview(_tmparray_lsubc)
            copyback_lsubc = True
            lsubc_ = _tmparray_lsubc
        else:
          if memview_lsubc.ndim != 1:
            raise TypeError("Argument lsubc must be one-dimensional")
          if memview_lsubc.format != "i":
            _tmparray_lsubc = array.array("i",lsubc)
            memview_lsubc = memoryview(_tmparray_lsubc)
            copyback_lsubc = True
            lsubc_ = _tmparray_lsubc
      if lvalc is None:
        raise TypeError("Argument lvalc may not be None")
      copyback_lvalc = False
      if lvalc is None:
        lvalc_ = None
        memview_lvalc = None
      else:
        try:
          memview_lvalc = memoryview(lvalc)
        except TypeError:
          try:
            _tmparray_lvalc = array.array("d",lvalc)
          except TypeError:
            raise TypeError("Argument lvalc has wrong type") from None
          else:
            memview_lvalc = memoryview(_tmparray_lvalc)
            copyback_lvalc = True
            lvalc_ = _tmparray_lvalc
        else:
          if memview_lvalc.ndim != 1:
            raise TypeError("Argument lvalc must be one-dimensional")
          if memview_lvalc.format != "d":
            _tmparray_lvalc = array.array("d",lvalc)
            memview_lvalc = memoryview(_tmparray_lvalc)
            copyback_lvalc = True
            lvalc_ = _tmparray_lvalc
      if b is None:
        raise TypeError("Argument b may not be None")
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",b)
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      _res_sparsetriangularsolvedense,_retargs_sparsetriangularsolvedense = self.__obj.sparsetriangularsolvedense_iOOOOO_7(transposed,memview_lnzc,memview_lptrc,memview_lsubc,memview_lvalc,memview_b)
      if _res_sparsetriangularsolvedense != 0:
        _,_msg_sparsetriangularsolvedense = self.__getlasterror(_res_sparsetriangularsolvedense)
        raise Error(rescode(_res_sparsetriangularsolvedense),_msg_sparsetriangularsolvedense)
      if copyback_b:
        for __tmp_1606 in range(len(b)): b[__tmp_1606] = b_[__tmp_1606]
    def sparsetriangularsolvedense(self,*args,**kwds):
      """
      Solves a sparse triangular system of linear equations.
    
      sparsetriangularsolvedense(transposed,lnzc,lptrc,lsubc,lvalc,b)
        [b : array(float64)]  The right-hand side of linear equation system to be solved as a dense vector.  
        [lnzc : array(int32)]  lnzc[j] is the number of nonzeros in column j.  
        [lptrc : array(int64)]  lptrc[j] is a pointer to the first row index and value in column j.  
        [lsubc : array(int32)]  Row indexes for each column stored sequentially.  
        [lvalc : array(float64)]  The value corresponding to row indexed stored lsubc.  
        [transposed : mosek.transpose]  Controls whether the solve is with L or the transposed L.  
      """
      return self.__sparsetriangularsolvedense_iOOOOO_7(*args,**kwds)
    def __potrf_iiO_4(self,uplo,n,a):
      if a is None:
        raise TypeError("Argument a may not be None")
      copyback_a = False
      if a is None:
        a_ = None
        memview_a = None
      else:
        try:
          memview_a = memoryview(a)
        except TypeError:
          try:
            _tmparray_a = array.array("d",a)
          except TypeError:
            raise TypeError("Argument a has wrong type") from None
          else:
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
        else:
          if memview_a.ndim != 1:
            raise TypeError("Argument a must be one-dimensional")
          if memview_a.format != "d":
            _tmparray_a = array.array("d",a)
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
      _res_potrf,_retargs_potrf = self.__obj.potrf_iiO_4(uplo,n,memview_a)
      if _res_potrf != 0:
        _,_msg_potrf = self.__getlasterror(_res_potrf)
        raise Error(rescode(_res_potrf),_msg_potrf)
      if copyback_a:
        for __tmp_1612 in range(len(a)): a[__tmp_1612] = a_[__tmp_1612]
    def potrf(self,*args,**kwds):
      """
      Computes a Cholesky factorization of a dense matrix.
    
      potrf(uplo,n,a)
        [a : array(float64)]  A symmetric matrix stored in column-major order.  
        [n : int32]  Dimension of the symmetric matrix.  
        [uplo : mosek.uplo]  Indicates whether the upper or lower triangular part of the matrix is stored.  
      """
      return self.__potrf_iiO_4(*args,**kwds)
    def __syeig_iiOO_5(self,uplo,n,a,w):
      if a is None:
        raise TypeError("Argument a may not be None")
      copyback_a = False
      if a is None:
        a_ = None
        memview_a = None
      else:
        try:
          memview_a = memoryview(a)
        except TypeError:
          try:
            _tmparray_a = array.array("d",a)
          except TypeError:
            raise TypeError("Argument a has wrong type") from None
          else:
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
        else:
          if memview_a.ndim != 1:
            raise TypeError("Argument a must be one-dimensional")
          if memview_a.format != "d":
            _tmparray_a = array.array("d",a)
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
      if w is None:
        raise TypeError("Argument w may not be None")
      copyback_w = False
      if w is None:
        w_ = None
        memview_w = None
      else:
        try:
          memview_w = memoryview(w)
        except TypeError:
          try:
            _tmparray_w = array.array("d",[0 for _ in range(len(w))])
          except TypeError:
            raise TypeError("Argument w has wrong type") from None
          else:
            memview_w = memoryview(_tmparray_w)
            copyback_w = True
            w_ = _tmparray_w
        else:
          if memview_w.ndim != 1:
            raise TypeError("Argument w must be one-dimensional")
          if memview_w.format != "d":
            _tmparray_w = array.array("d",w)
            memview_w = memoryview(_tmparray_w)
            copyback_w = True
            w_ = _tmparray_w
      _res_syeig,_retargs_syeig = self.__obj.syeig_iiOO_5(uplo,n,memview_a,memview_w)
      if _res_syeig != 0:
        _,_msg_syeig = self.__getlasterror(_res_syeig)
        raise Error(rescode(_res_syeig),_msg_syeig)
      if copyback_w:
        for __tmp_1615 in range(len(w)): w[__tmp_1615] = w_[__tmp_1615]
    def __syeig_iiOO_4(self,uplo,n,a):
      if a is None:
        raise TypeError("Argument a may not be None")
      copyback_a = False
      if a is None:
        a_ = None
        memview_a = None
      else:
        try:
          memview_a = memoryview(a)
        except TypeError:
          try:
            _tmparray_a = array.array("d",a)
          except TypeError:
            raise TypeError("Argument a has wrong type") from None
          else:
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
        else:
          if memview_a.ndim != 1:
            raise TypeError("Argument a must be one-dimensional")
          if memview_a.format != "d":
            _tmparray_a = array.array("d",a)
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
      w_ = bytearray(0)
      _res_syeig,_retargs_syeig = self.__obj.syeig_iiOO_4(uplo,n,memview_a,w_)
      if _res_syeig != 0:
        _,_msg_syeig = self.__getlasterror(_res_syeig)
        raise Error(rescode(_res_syeig),_msg_syeig)
      w = array.array("d")
      w.frombytes(w_)
      return (w)
    def syeig(self,*args,**kwds):
      """
      Computes all eigenvalues of a symmetric dense matrix.
    
      syeig(uplo,n,a,w)
      syeig(uplo,n,a) -> (w)
        [a : array(float64)]  Input matrix A.  
        [n : int32]  Dimension of the symmetric input matrix.  
        [uplo : mosek.uplo]  Indicates whether the upper or lower triangular part is used.  
        [w : array(float64)]  Array of length at least n containing the eigenvalues of A.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__syeig_iiOO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__syeig_iiOO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __syevd_iiOO_5(self,uplo,n,a,w):
      if a is None:
        raise TypeError("Argument a may not be None")
      copyback_a = False
      if a is None:
        a_ = None
        memview_a = None
      else:
        try:
          memview_a = memoryview(a)
        except TypeError:
          try:
            _tmparray_a = array.array("d",a)
          except TypeError:
            raise TypeError("Argument a has wrong type") from None
          else:
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
        else:
          if memview_a.ndim != 1:
            raise TypeError("Argument a must be one-dimensional")
          if memview_a.format != "d":
            _tmparray_a = array.array("d",a)
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
      if w is None:
        raise TypeError("Argument w may not be None")
      copyback_w = False
      if w is None:
        w_ = None
        memview_w = None
      else:
        try:
          memview_w = memoryview(w)
        except TypeError:
          try:
            _tmparray_w = array.array("d",[0 for _ in range(len(w))])
          except TypeError:
            raise TypeError("Argument w has wrong type") from None
          else:
            memview_w = memoryview(_tmparray_w)
            copyback_w = True
            w_ = _tmparray_w
        else:
          if memview_w.ndim != 1:
            raise TypeError("Argument w must be one-dimensional")
          if memview_w.format != "d":
            _tmparray_w = array.array("d",w)
            memview_w = memoryview(_tmparray_w)
            copyback_w = True
            w_ = _tmparray_w
      _res_syevd,_retargs_syevd = self.__obj.syevd_iiOO_5(uplo,n,memview_a,memview_w)
      if _res_syevd != 0:
        _,_msg_syevd = self.__getlasterror(_res_syevd)
        raise Error(rescode(_res_syevd),_msg_syevd)
      if copyback_a:
        for __tmp_1618 in range(len(a)): a[__tmp_1618] = a_[__tmp_1618]
      if copyback_w:
        for __tmp_1619 in range(len(w)): w[__tmp_1619] = w_[__tmp_1619]
    def __syevd_iiOO_4(self,uplo,n,a):
      if a is None:
        raise TypeError("Argument a may not be None")
      copyback_a = False
      if a is None:
        a_ = None
        memview_a = None
      else:
        try:
          memview_a = memoryview(a)
        except TypeError:
          try:
            _tmparray_a = array.array("d",a)
          except TypeError:
            raise TypeError("Argument a has wrong type") from None
          else:
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
        else:
          if memview_a.ndim != 1:
            raise TypeError("Argument a must be one-dimensional")
          if memview_a.format != "d":
            _tmparray_a = array.array("d",a)
            memview_a = memoryview(_tmparray_a)
            copyback_a = True
            a_ = _tmparray_a
      w_ = bytearray(0)
      _res_syevd,_retargs_syevd = self.__obj.syevd_iiOO_4(uplo,n,memview_a,w_)
      if _res_syevd != 0:
        _,_msg_syevd = self.__getlasterror(_res_syevd)
        raise Error(rescode(_res_syevd),_msg_syevd)
      if copyback_a:
        for __tmp_1620 in range(len(a)): a[__tmp_1620] = a_[__tmp_1620]
      w = array.array("d")
      w.frombytes(w_)
      return (w)
    def syevd(self,*args,**kwds):
      """
      Computes all the eigenvalues and eigenvectors of a symmetric dense matrix, and thus its eigenvalue decomposition.
    
      syevd(uplo,n,a,w)
      syevd(uplo,n,a) -> (w)
        [a : array(float64)]  Input matrix A.  
        [n : int32]  Dimension of the symmetric input matrix.  
        [uplo : mosek.uplo]  Indicates whether the upper or lower triangular part is used.  
        [w : array(float64)]  Array of length at least n containing the eigenvalues of A.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__syevd_iiOO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__syevd_iiOO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    @staticmethod
    def __licensecleanup__0():
      _res_licensecleanup,_retargs_licensecleanup = _msk.Env.licensecleanup__0()
      if _res_licensecleanup != 0:
        raise Error(rescode(_res_licensecleanup),"")
    @staticmethod
    def licensecleanup(*args,**kwds):
      """
      Stops all threads and delete all handles used by the license system.
    
      licensecleanup()
      """
      return Env.__licensecleanup__0(*args,**kwds)


class Task:
    def __init__(self,env=None,numcon=0,numvar=0):
        if env is None:
            self.__obj = _msk.Task(None,numcon,numvar)
        elif isinstance(env,Task):
            self.__obj = _msk.Task(None,numcon,numvar,other=env._Task__obj)
        elif isinstance(env, _msk.Task):
            self.__obj = env
        elif env is None:
            self.__obj = _msk.Task(None,numcon,numvar)
        else:
            self.__obj = _msk.Task(env._Env__obj,numcon,numvar)

    def __del__(self):
        try:
            o = self.__obj
        except AttributeError:
            pass
        else:
            o.dispose()
            del self.__obj

    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        self.__del__()

    def __getlasterror(self,res):
        res,msg = self.__obj.getlasterror()
        return rescode(res),msg

    def set_Stream(self,whichstream,func):
        if isinstance(whichstream, streamtype):
            if func is None:
                self.__obj.remove_Stream(whichstream)
            else:
                self.__obj.set_Stream(whichstream,func)
        else:
            raise TypeError("Invalid stream %s" % whichstream)

    def set_Progress(self,func):
        """
        Set the progress callback function. If func is None, progress callbacks are detached and disabled.
        """
        self.__obj.set_Progress(func)

    def set_InfoCallback(self,func):
        """
        Set the progress callback function. If func is None, progress callbacks are detached and disabled.
        """
        self.__obj.set_InfoCallback(func)

    def writedatastream(self,dformat,compress,stream):
        """
        Writes the problem data in specified format to a stream
        """
        if not isinstance(dformat, dataformat):
            raise TypeError("Invalid data format %s" % dformat)
        if not isinstance(compress,compresstype):
          raise TypeError("Invalid compression format %s" % compress)

        res = self.__obj.writedatastream(dformat,compress,stream)
        if res != 0:
            _,msg = self.__getlasterror(res)
            raise Error(rescode(res),msg)



    def __analyzeproblem_i_2(self,whichstream):
      _res_analyzeproblem,_retargs_analyzeproblem = self.__obj.analyzeproblem_i_2(whichstream)
      if _res_analyzeproblem != 0:
        _,_msg_analyzeproblem = self.__getlasterror(_res_analyzeproblem)
        raise Error(rescode(_res_analyzeproblem),_msg_analyzeproblem)
    def analyzeproblem(self,*args,**kwds):
      """
      Analyze the data of a task.
    
      analyzeproblem(whichstream)
        [whichstream : mosek.streamtype]  Index of the stream.  
      """
      return self.__analyzeproblem_i_2(*args,**kwds)
    def __analyzenames_ii_3(self,whichstream,nametype):
      _res_analyzenames,_retargs_analyzenames = self.__obj.analyzenames_ii_3(whichstream,nametype)
      if _res_analyzenames != 0:
        _,_msg_analyzenames = self.__getlasterror(_res_analyzenames)
        raise Error(rescode(_res_analyzenames),_msg_analyzenames)
    def analyzenames(self,*args,**kwds):
      """
      Analyze the names and issue an error for the first invalid name.
    
      analyzenames(whichstream,nametype)
        [nametype : mosek.nametype]  The type of names e.g. valid in MPS or LP files.  
        [whichstream : mosek.streamtype]  Index of the stream.  
      """
      return self.__analyzenames_ii_3(*args,**kwds)
    def __analyzesolution_ii_3(self,whichstream,whichsol):
      _res_analyzesolution,_retargs_analyzesolution = self.__obj.analyzesolution_ii_3(whichstream,whichsol)
      if _res_analyzesolution != 0:
        _,_msg_analyzesolution = self.__getlasterror(_res_analyzesolution)
        raise Error(rescode(_res_analyzesolution),_msg_analyzesolution)
    def analyzesolution(self,*args,**kwds):
      """
      Print information related to the quality of the solution.
    
      analyzesolution(whichstream,whichsol)
        [whichsol : mosek.soltype]  Selects a solution.  
        [whichstream : mosek.streamtype]  Index of the stream.  
      """
      return self.__analyzesolution_ii_3(*args,**kwds)
    def __initbasissolve_O_2(self,basis):
      copyback_basis = False
      if basis is None:
        basis_ = None
        memview_basis = None
      else:
        try:
          memview_basis = memoryview(basis)
        except TypeError:
          try:
            _tmparray_basis = array.array("i",[0 for _ in range(len(basis))])
          except TypeError:
            raise TypeError("Argument basis has wrong type") from None
          else:
            memview_basis = memoryview(_tmparray_basis)
            copyback_basis = True
            basis_ = _tmparray_basis
        else:
          if memview_basis.ndim != 1:
            raise TypeError("Argument basis must be one-dimensional")
          if memview_basis.format != "i":
            _tmparray_basis = array.array("i",basis)
            memview_basis = memoryview(_tmparray_basis)
            copyback_basis = True
            basis_ = _tmparray_basis
      _res_initbasissolve,_retargs_initbasissolve = self.__obj.initbasissolve_O_2(memview_basis)
      if _res_initbasissolve != 0:
        _,_msg_initbasissolve = self.__getlasterror(_res_initbasissolve)
        raise Error(rescode(_res_initbasissolve),_msg_initbasissolve)
      if copyback_basis:
        for __tmp_2 in range(len(basis)): basis[__tmp_2] = basis_[__tmp_2]
    def __initbasissolve_O_1(self):
      basis_ = bytearray(0)
      _res_initbasissolve,_retargs_initbasissolve = self.__obj.initbasissolve_O_1(basis_)
      if _res_initbasissolve != 0:
        _,_msg_initbasissolve = self.__getlasterror(_res_initbasissolve)
        raise Error(rescode(_res_initbasissolve),_msg_initbasissolve)
      basis = array.array("i")
      basis.frombytes(basis_)
      return (basis)
    def initbasissolve(self,*args,**kwds):
      """
      Prepare a task for basis solver.
    
      initbasissolve(basis)
      initbasissolve() -> (basis)
        [basis : array(int32)]  The array of basis indexes to use.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 2: return self.__initbasissolve_O_2(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__initbasissolve_O_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __solvewithbasis_iiOO_5(self,transp,numnz,sub,val):
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",val)
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_solvewithbasis,_retargs_solvewithbasis = self.__obj.solvewithbasis_iiOO_5(transp,numnz,memview_sub,memview_val)
      if _res_solvewithbasis != 0:
        _,_msg_solvewithbasis = self.__getlasterror(_res_solvewithbasis)
        raise Error(rescode(_res_solvewithbasis),_msg_solvewithbasis)
      else:
        (numnzout) = _retargs_solvewithbasis
      if copyback_sub:
        for __tmp_8 in range(len(sub)): sub[__tmp_8] = sub_[__tmp_8]
      if copyback_val:
        for __tmp_11 in range(len(val)): val[__tmp_11] = val_[__tmp_11]
      return (numnzout)
    def solvewithbasis(self,*args,**kwds):
      """
      Solve a linear equation system involving a basis matrix.
    
      solvewithbasis(transp,numnz,sub,val) -> (numnzout)
        [numnz : int32]  Input (number of non-zeros in right-hand side).  
        [numnzout : int32]  Output (number of non-zeros in solution vector).  
        [sub : array(int32)]  Input (indexes of non-zeros in right-hand side) and output (indexes of non-zeros in solution vector).  
        [transp : bool]  Controls which problem formulation is solved.  
        [val : array(float64)]  Input (right-hand side values) and output (solution vector values).  
      """
      return self.__solvewithbasis_iiOO_5(*args,**kwds)
    def __basiscond__1(self):
      _res_basiscond,_retargs_basiscond = self.__obj.basiscond__1()
      if _res_basiscond != 0:
        _,_msg_basiscond = self.__getlasterror(_res_basiscond)
        raise Error(rescode(_res_basiscond),_msg_basiscond)
      else:
        (nrmbasis,nrminvbasis) = _retargs_basiscond
      return (nrmbasis,nrminvbasis)
    def basiscond(self,*args,**kwds):
      """
      Computes conditioning information for the basis matrix.
    
      basiscond() -> (nrmbasis,nrminvbasis)
        [nrmbasis : float64]  An estimate for the 1-norm of the basis.  
        [nrminvbasis : float64]  An estimate for the 1-norm of the inverse of the basis.  
      """
      return self.__basiscond__1(*args,**kwds)
    def __appendcons_i_2(self,num):
      _res_appendcons,_retargs_appendcons = self.__obj.appendcons_i_2(num)
      if _res_appendcons != 0:
        _,_msg_appendcons = self.__getlasterror(_res_appendcons)
        raise Error(rescode(_res_appendcons),_msg_appendcons)
    def appendcons(self,*args,**kwds):
      """
      Appends a number of constraints to the optimization task.
    
      appendcons(num)
        [num : int32]  Number of constraints which should be appended.  
      """
      return self.__appendcons_i_2(*args,**kwds)
    def __appendvars_i_2(self,num):
      _res_appendvars,_retargs_appendvars = self.__obj.appendvars_i_2(num)
      if _res_appendvars != 0:
        _,_msg_appendvars = self.__getlasterror(_res_appendvars)
        raise Error(rescode(_res_appendvars),_msg_appendvars)
    def appendvars(self,*args,**kwds):
      """
      Appends a number of variables to the optimization task.
    
      appendvars(num)
        [num : int32]  Number of variables which should be appended.  
      """
      return self.__appendvars_i_2(*args,**kwds)
    def __removecons_O_2(self,subset):
      if subset is None:
        raise TypeError("Argument subset may not be None")
      copyback_subset = False
      if subset is None:
        subset_ = None
        memview_subset = None
      else:
        try:
          memview_subset = memoryview(subset)
        except TypeError:
          try:
            _tmparray_subset = array.array("i",subset)
          except TypeError:
            raise TypeError("Argument subset has wrong type") from None
          else:
            memview_subset = memoryview(_tmparray_subset)
            copyback_subset = True
            subset_ = _tmparray_subset
        else:
          if memview_subset.ndim != 1:
            raise TypeError("Argument subset must be one-dimensional")
          if memview_subset.format != "i":
            _tmparray_subset = array.array("i",subset)
            memview_subset = memoryview(_tmparray_subset)
            copyback_subset = True
            subset_ = _tmparray_subset
      _res_removecons,_retargs_removecons = self.__obj.removecons_O_2(memview_subset)
      if _res_removecons != 0:
        _,_msg_removecons = self.__getlasterror(_res_removecons)
        raise Error(rescode(_res_removecons),_msg_removecons)
    def removecons(self,*args,**kwds):
      """
      Removes a number of constraints.
    
      removecons(subset)
        [subset : array(int32)]  Indexes of constraints which should be removed.  
      """
      return self.__removecons_O_2(*args,**kwds)
    def __removevars_O_2(self,subset):
      if subset is None:
        raise TypeError("Argument subset may not be None")
      copyback_subset = False
      if subset is None:
        subset_ = None
        memview_subset = None
      else:
        try:
          memview_subset = memoryview(subset)
        except TypeError:
          try:
            _tmparray_subset = array.array("i",subset)
          except TypeError:
            raise TypeError("Argument subset has wrong type") from None
          else:
            memview_subset = memoryview(_tmparray_subset)
            copyback_subset = True
            subset_ = _tmparray_subset
        else:
          if memview_subset.ndim != 1:
            raise TypeError("Argument subset must be one-dimensional")
          if memview_subset.format != "i":
            _tmparray_subset = array.array("i",subset)
            memview_subset = memoryview(_tmparray_subset)
            copyback_subset = True
            subset_ = _tmparray_subset
      _res_removevars,_retargs_removevars = self.__obj.removevars_O_2(memview_subset)
      if _res_removevars != 0:
        _,_msg_removevars = self.__getlasterror(_res_removevars)
        raise Error(rescode(_res_removevars),_msg_removevars)
    def removevars(self,*args,**kwds):
      """
      Removes a number of variables.
    
      removevars(subset)
        [subset : array(int32)]  Indexes of variables which should be removed.  
      """
      return self.__removevars_O_2(*args,**kwds)
    def __removebarvars_O_2(self,subset):
      if subset is None:
        raise TypeError("Argument subset may not be None")
      copyback_subset = False
      if subset is None:
        subset_ = None
        memview_subset = None
      else:
        try:
          memview_subset = memoryview(subset)
        except TypeError:
          try:
            _tmparray_subset = array.array("i",subset)
          except TypeError:
            raise TypeError("Argument subset has wrong type") from None
          else:
            memview_subset = memoryview(_tmparray_subset)
            copyback_subset = True
            subset_ = _tmparray_subset
        else:
          if memview_subset.ndim != 1:
            raise TypeError("Argument subset must be one-dimensional")
          if memview_subset.format != "i":
            _tmparray_subset = array.array("i",subset)
            memview_subset = memoryview(_tmparray_subset)
            copyback_subset = True
            subset_ = _tmparray_subset
      _res_removebarvars,_retargs_removebarvars = self.__obj.removebarvars_O_2(memview_subset)
      if _res_removebarvars != 0:
        _,_msg_removebarvars = self.__getlasterror(_res_removebarvars)
        raise Error(rescode(_res_removebarvars),_msg_removebarvars)
    def removebarvars(self,*args,**kwds):
      """
      Removes a number of symmetric matrices.
    
      removebarvars(subset)
        [subset : array(int32)]  Indexes of symmetric matrices which should be removed.  
      """
      return self.__removebarvars_O_2(*args,**kwds)
    def __removecones_O_2(self,subset):
      if subset is None:
        raise TypeError("Argument subset may not be None")
      copyback_subset = False
      if subset is None:
        subset_ = None
        memview_subset = None
      else:
        try:
          memview_subset = memoryview(subset)
        except TypeError:
          try:
            _tmparray_subset = array.array("i",subset)
          except TypeError:
            raise TypeError("Argument subset has wrong type") from None
          else:
            memview_subset = memoryview(_tmparray_subset)
            copyback_subset = True
            subset_ = _tmparray_subset
        else:
          if memview_subset.ndim != 1:
            raise TypeError("Argument subset must be one-dimensional")
          if memview_subset.format != "i":
            _tmparray_subset = array.array("i",subset)
            memview_subset = memoryview(_tmparray_subset)
            copyback_subset = True
            subset_ = _tmparray_subset
      _res_removecones,_retargs_removecones = self.__obj.removecones_O_2(memview_subset)
      if _res_removecones != 0:
        _,_msg_removecones = self.__getlasterror(_res_removecones)
        raise Error(rescode(_res_removecones),_msg_removecones)
    def removecones(self,*args,**kwds):
      """
      Removes a number of conic constraints from the problem.
    
      removecones(subset)
        [subset : array(int32)]  Indexes of cones which should be removed.  
      """
      return self.__removecones_O_2(*args,**kwds)
    def __appendbarvars_O_2(self,dim):
      if dim is None:
        raise TypeError("Argument dim may not be None")
      copyback_dim = False
      if dim is None:
        dim_ = None
        memview_dim = None
      else:
        try:
          memview_dim = memoryview(dim)
        except TypeError:
          try:
            _tmparray_dim = array.array("i",dim)
          except TypeError:
            raise TypeError("Argument dim has wrong type") from None
          else:
            memview_dim = memoryview(_tmparray_dim)
            copyback_dim = True
            dim_ = _tmparray_dim
        else:
          if memview_dim.ndim != 1:
            raise TypeError("Argument dim must be one-dimensional")
          if memview_dim.format != "i":
            _tmparray_dim = array.array("i",dim)
            memview_dim = memoryview(_tmparray_dim)
            copyback_dim = True
            dim_ = _tmparray_dim
      _res_appendbarvars,_retargs_appendbarvars = self.__obj.appendbarvars_O_2(memview_dim)
      if _res_appendbarvars != 0:
        _,_msg_appendbarvars = self.__getlasterror(_res_appendbarvars)
        raise Error(rescode(_res_appendbarvars),_msg_appendbarvars)
    def appendbarvars(self,*args,**kwds):
      """
      Appends semidefinite variables to the problem.
    
      appendbarvars(dim)
        [dim : array(int32)]  Dimensions of symmetric matrix variables to be added.  
      """
      return self.__appendbarvars_O_2(*args,**kwds)
    def __appendcone_idO_4(self,ct,conepar,submem):
      if submem is None:
        raise TypeError("Argument submem may not be None")
      copyback_submem = False
      if submem is None:
        submem_ = None
        memview_submem = None
      else:
        try:
          memview_submem = memoryview(submem)
        except TypeError:
          try:
            _tmparray_submem = array.array("i",submem)
          except TypeError:
            raise TypeError("Argument submem has wrong type") from None
          else:
            memview_submem = memoryview(_tmparray_submem)
            copyback_submem = True
            submem_ = _tmparray_submem
        else:
          if memview_submem.ndim != 1:
            raise TypeError("Argument submem must be one-dimensional")
          if memview_submem.format != "i":
            _tmparray_submem = array.array("i",submem)
            memview_submem = memoryview(_tmparray_submem)
            copyback_submem = True
            submem_ = _tmparray_submem
      _res_appendcone,_retargs_appendcone = self.__obj.appendcone_idO_4(ct,conepar,memview_submem)
      if _res_appendcone != 0:
        _,_msg_appendcone = self.__getlasterror(_res_appendcone)
        raise Error(rescode(_res_appendcone),_msg_appendcone)
    def appendcone(self,*args,**kwds):
      """
      Appends a new conic constraint to the problem.
    
      appendcone(ct,conepar,submem)
        [conepar : float64]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
        [ct : mosek.conetype]  Specifies the type of the cone.  
        [submem : array(int32)]  Variable subscripts of the members in the cone.  
      """
      return self.__appendcone_idO_4(*args,**kwds)
    def __appendconeseq_idii_5(self,ct,conepar,nummem,j):
      _res_appendconeseq,_retargs_appendconeseq = self.__obj.appendconeseq_idii_5(ct,conepar,nummem,j)
      if _res_appendconeseq != 0:
        _,_msg_appendconeseq = self.__getlasterror(_res_appendconeseq)
        raise Error(rescode(_res_appendconeseq),_msg_appendconeseq)
    def appendconeseq(self,*args,**kwds):
      """
      Appends a new conic constraint to the problem.
    
      appendconeseq(ct,conepar,nummem,j)
        [conepar : float64]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
        [ct : mosek.conetype]  Specifies the type of the cone.  
        [j : int32]  Index of the first variable in the conic constraint.  
        [nummem : int32]  Number of member variables in the cone.  
      """
      return self.__appendconeseq_idii_5(*args,**kwds)
    def __appendconesseq_OOOi_5(self,ct,conepar,nummem,j):
      if ct is None:
        ct_ = None
      else:
        # i
        _tmparray_ct_ = array.array("i",ct)
        ct_ = memoryview(_tmparray_ct_)
      if conepar is None:
        raise TypeError("Argument conepar may not be None")
      copyback_conepar = False
      if conepar is None:
        conepar_ = None
        memview_conepar = None
      else:
        try:
          memview_conepar = memoryview(conepar)
        except TypeError:
          try:
            _tmparray_conepar = array.array("d",conepar)
          except TypeError:
            raise TypeError("Argument conepar has wrong type") from None
          else:
            memview_conepar = memoryview(_tmparray_conepar)
            copyback_conepar = True
            conepar_ = _tmparray_conepar
        else:
          if memview_conepar.ndim != 1:
            raise TypeError("Argument conepar must be one-dimensional")
          if memview_conepar.format != "d":
            _tmparray_conepar = array.array("d",conepar)
            memview_conepar = memoryview(_tmparray_conepar)
            copyback_conepar = True
            conepar_ = _tmparray_conepar
      if nummem is None:
        raise TypeError("Argument nummem may not be None")
      copyback_nummem = False
      if nummem is None:
        nummem_ = None
        memview_nummem = None
      else:
        try:
          memview_nummem = memoryview(nummem)
        except TypeError:
          try:
            _tmparray_nummem = array.array("i",nummem)
          except TypeError:
            raise TypeError("Argument nummem has wrong type") from None
          else:
            memview_nummem = memoryview(_tmparray_nummem)
            copyback_nummem = True
            nummem_ = _tmparray_nummem
        else:
          if memview_nummem.ndim != 1:
            raise TypeError("Argument nummem must be one-dimensional")
          if memview_nummem.format != "i":
            _tmparray_nummem = array.array("i",nummem)
            memview_nummem = memoryview(_tmparray_nummem)
            copyback_nummem = True
            nummem_ = _tmparray_nummem
      _res_appendconesseq,_retargs_appendconesseq = self.__obj.appendconesseq_OOOi_5(ct_,memview_conepar,memview_nummem,j)
      if _res_appendconesseq != 0:
        _,_msg_appendconesseq = self.__getlasterror(_res_appendconesseq)
        raise Error(rescode(_res_appendconesseq),_msg_appendconesseq)
    def appendconesseq(self,*args,**kwds):
      """
      Appends multiple conic constraints to the problem.
    
      appendconesseq(ct,conepar,nummem,j)
        [conepar : array(float64)]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
        [ct : array(mosek.conetype)]  Specifies the type of the cone.  
        [j : int32]  Index of the first variable in the first cone to be appended.  
        [nummem : array(int32)]  Numbers of member variables in the cones.  
      """
      return self.__appendconesseq_OOOi_5(*args,**kwds)
    def __chgconbound_iiid_5(self,i,lower,finite,value):
      _res_chgconbound,_retargs_chgconbound = self.__obj.chgconbound_iiid_5(i,lower,finite,value)
      if _res_chgconbound != 0:
        _,_msg_chgconbound = self.__getlasterror(_res_chgconbound)
        raise Error(rescode(_res_chgconbound),_msg_chgconbound)
    def chgconbound(self,*args,**kwds):
      """
      Changes the bounds for one constraint.
    
      chgconbound(i,lower,finite,value)
        [finite : int32]  If non-zero, then the given value is assumed to be finite.  
        [i : int32]  Index of the constraint for which the bounds should be changed.  
        [lower : int32]  If non-zero, then the lower bound is changed, otherwise the upper bound is changed.  
        [value : float64]  New value for the bound.  
      """
      return self.__chgconbound_iiid_5(*args,**kwds)
    def __chgvarbound_iiid_5(self,j,lower,finite,value):
      _res_chgvarbound,_retargs_chgvarbound = self.__obj.chgvarbound_iiid_5(j,lower,finite,value)
      if _res_chgvarbound != 0:
        _,_msg_chgvarbound = self.__getlasterror(_res_chgvarbound)
        raise Error(rescode(_res_chgvarbound),_msg_chgvarbound)
    def chgvarbound(self,*args,**kwds):
      """
      Changes the bounds for one variable.
    
      chgvarbound(j,lower,finite,value)
        [finite : int32]  If non-zero, then the given value is assumed to be finite.  
        [j : int32]  Index of the variable for which the bounds should be changed.  
        [lower : int32]  If non-zero, then the lower bound is changed, otherwise the upper bound is changed.  
        [value : float64]  New value for the bound.  
      """
      return self.__chgvarbound_iiid_5(*args,**kwds)
    def __getaij_ii_3(self,i,j):
      _res_getaij,_retargs_getaij = self.__obj.getaij_ii_3(i,j)
      if _res_getaij != 0:
        _,_msg_getaij = self.__getlasterror(_res_getaij)
        raise Error(rescode(_res_getaij),_msg_getaij)
      else:
        (aij) = _retargs_getaij
      return (aij)
    def getaij(self,*args,**kwds):
      """
      Obtains a single coefficient in linear constraint matrix.
    
      getaij(i,j) -> (aij)
        [aij : float64]  Returns the requested coefficient.  
        [i : int32]  Row index of the coefficient to be returned.  
        [j : int32]  Column index of the coefficient to be returned.  
      """
      return self.__getaij_ii_3(*args,**kwds)
    def __getapiecenumnz_iiii_5(self,firsti,lasti,firstj,lastj):
      _res_getapiecenumnz,_retargs_getapiecenumnz = self.__obj.getapiecenumnz_iiii_5(firsti,lasti,firstj,lastj)
      if _res_getapiecenumnz != 0:
        _,_msg_getapiecenumnz = self.__getlasterror(_res_getapiecenumnz)
        raise Error(rescode(_res_getapiecenumnz),_msg_getapiecenumnz)
      else:
        (numnz) = _retargs_getapiecenumnz
      return (numnz)
    def getapiecenumnz(self,*args,**kwds):
      """
      Obtains the number non-zeros in a rectangular piece of the linear constraint matrix.
    
      getapiecenumnz(firsti,lasti,firstj,lastj) -> (numnz)
        [firsti : int32]  Index of the first row in the rectangular piece.  
        [firstj : int32]  Index of the first column in the rectangular piece.  
        [lasti : int32]  Index of the last row plus one in the rectangular piece.  
        [lastj : int32]  Index of the last column plus one in the rectangular piece.  
        [numnz : int32]  Number of non-zero elements in the rectangular piece of the linear constraint matrix.  
      """
      return self.__getapiecenumnz_iiii_5(*args,**kwds)
    def __getacolnumnz_i_2(self,i):
      _res_getacolnumnz,_retargs_getacolnumnz = self.__obj.getacolnumnz_i_2(i)
      if _res_getacolnumnz != 0:
        _,_msg_getacolnumnz = self.__getlasterror(_res_getacolnumnz)
        raise Error(rescode(_res_getacolnumnz),_msg_getacolnumnz)
      else:
        (nzj) = _retargs_getacolnumnz
      return (nzj)
    def getacolnumnz(self,*args,**kwds):
      """
      Obtains the number of non-zero elements in one column of the linear constraint matrix
    
      getacolnumnz(i) -> (nzj)
        [i : int32]  Index of the column.  
        [nzj : int32]  Number of non-zeros in the j'th column of (A).  
      """
      return self.__getacolnumnz_i_2(*args,**kwds)
    def __getacol_iOO_4(self,j,subj,valj):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",[0 for _ in range(len(subj))])
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if valj is None:
        raise TypeError("Argument valj may not be None")
      copyback_valj = False
      if valj is None:
        valj_ = None
        memview_valj = None
      else:
        try:
          memview_valj = memoryview(valj)
        except TypeError:
          try:
            _tmparray_valj = array.array("d",[0 for _ in range(len(valj))])
          except TypeError:
            raise TypeError("Argument valj has wrong type") from None
          else:
            memview_valj = memoryview(_tmparray_valj)
            copyback_valj = True
            valj_ = _tmparray_valj
        else:
          if memview_valj.ndim != 1:
            raise TypeError("Argument valj must be one-dimensional")
          if memview_valj.format != "d":
            _tmparray_valj = array.array("d",valj)
            memview_valj = memoryview(_tmparray_valj)
            copyback_valj = True
            valj_ = _tmparray_valj
      _res_getacol,_retargs_getacol = self.__obj.getacol_iOO_4(j,memview_subj,memview_valj)
      if _res_getacol != 0:
        _,_msg_getacol = self.__getlasterror(_res_getacol)
        raise Error(rescode(_res_getacol),_msg_getacol)
      else:
        (nzj) = _retargs_getacol
      if copyback_subj:
        for __tmp_38 in range(len(subj)): subj[__tmp_38] = subj_[__tmp_38]
      if copyback_valj:
        for __tmp_41 in range(len(valj)): valj[__tmp_41] = valj_[__tmp_41]
      return (nzj)
    def __getacol_iOO_2(self,j):
      subj_ = bytearray(0)
      valj_ = bytearray(0)
      _res_getacol,_retargs_getacol = self.__obj.getacol_iOO_2(j,subj_,valj_)
      if _res_getacol != 0:
        _,_msg_getacol = self.__getlasterror(_res_getacol)
        raise Error(rescode(_res_getacol),_msg_getacol)
      else:
        (nzj) = _retargs_getacol
      subj = array.array("i")
      subj.frombytes(subj_)
      valj = array.array("d")
      valj.frombytes(valj_)
      return (nzj,subj,valj)
    def getacol(self,*args,**kwds):
      """
      Obtains one column of the linear constraint matrix.
    
      getacol(j,subj,valj) -> (nzj)
      getacol(j) -> (nzj,subj,valj)
        [j : int32]  Index of the column.  
        [nzj : int32]  Number of non-zeros in the column obtained.  
        [subj : array(int32)]  Row indices of the non-zeros in the column obtained.  
        [valj : array(float64)]  Numerical values in the column obtained.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getacol_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getacol_iOO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getacolslice64_iiOOOO_7(self,first,last,ptrb,ptre,sub,val):
      if ptrb is None:
        raise TypeError("Argument ptrb may not be None")
      copyback_ptrb = False
      if ptrb is None:
        ptrb_ = None
        memview_ptrb = None
      else:
        try:
          memview_ptrb = memoryview(ptrb)
        except TypeError:
          try:
            _tmparray_ptrb = array.array("q",[0 for _ in range(len(ptrb))])
          except TypeError:
            raise TypeError("Argument ptrb has wrong type") from None
          else:
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
        else:
          if memview_ptrb.ndim != 1:
            raise TypeError("Argument ptrb must be one-dimensional")
          if memview_ptrb.format != "q":
            _tmparray_ptrb = array.array("q",ptrb)
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
      if ptre is None:
        raise TypeError("Argument ptre may not be None")
      copyback_ptre = False
      if ptre is None:
        ptre_ = None
        memview_ptre = None
      else:
        try:
          memview_ptre = memoryview(ptre)
        except TypeError:
          try:
            _tmparray_ptre = array.array("q",[0 for _ in range(len(ptre))])
          except TypeError:
            raise TypeError("Argument ptre has wrong type") from None
          else:
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
        else:
          if memview_ptre.ndim != 1:
            raise TypeError("Argument ptre must be one-dimensional")
          if memview_ptre.format != "q":
            _tmparray_ptre = array.array("q",ptre)
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",[0 for _ in range(len(sub))])
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if val is None:
        raise TypeError("Argument val may not be None")
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",[0 for _ in range(len(val))])
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_getacolslice64,_retargs_getacolslice64 = self.__obj.getacolslice64_iiOOOO_7(first,last,memview_ptrb,memview_ptre,memview_sub,memview_val)
      if _res_getacolslice64 != 0:
        _,_msg_getacolslice64 = self.__getlasterror(_res_getacolslice64)
        raise Error(rescode(_res_getacolslice64),_msg_getacolslice64)
      if copyback_ptrb:
        for __tmp_50 in range(len(ptrb)): ptrb[__tmp_50] = ptrb_[__tmp_50]
      if copyback_ptre:
        for __tmp_51 in range(len(ptre)): ptre[__tmp_51] = ptre_[__tmp_51]
      if copyback_sub:
        for __tmp_52 in range(len(sub)): sub[__tmp_52] = sub_[__tmp_52]
      if copyback_val:
        for __tmp_53 in range(len(val)): val[__tmp_53] = val_[__tmp_53]
    def __getacolslice64_iiOOOO_3(self,first,last):
      ptrb_ = bytearray(0)
      ptre_ = bytearray(0)
      sub_ = bytearray(0)
      val_ = bytearray(0)
      _res_getacolslice64,_retargs_getacolslice64 = self.__obj.getacolslice64_iiOOOO_3(first,last,ptrb_,ptre_,sub_,val_)
      if _res_getacolslice64 != 0:
        _,_msg_getacolslice64 = self.__getlasterror(_res_getacolslice64)
        raise Error(rescode(_res_getacolslice64),_msg_getacolslice64)
      ptrb = array.array("q")
      ptrb.frombytes(ptrb_)
      ptre = array.array("q")
      ptre.frombytes(ptre_)
      sub = array.array("i")
      sub.frombytes(sub_)
      val = array.array("d")
      val.frombytes(val_)
      return (ptrb,ptre,sub,val)
    def getacolslice(self,*args,**kwds):
      """
      Obtains a sequence of columns from the coefficient matrix.
    
      getacolslice(first,last,ptrb,ptre,sub,val)
      getacolslice(first,last) -> (ptrb,ptre,sub,val)
        [first : int32]  Index of the first column in the sequence.  
        [last : int32]  Index of the last column in the sequence plus one.  
        [ptrb : array(int64)]  Column start pointers.  
        [ptre : array(int64)]  Column end pointers.  
        [sub : array(int32)]  Contains the row subscripts.  
        [val : array(float64)]  Contains the coefficient values.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 7: return self.__getacolslice64_iiOOOO_7(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getacolslice64_iiOOOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getarownumnz_i_2(self,i):
      _res_getarownumnz,_retargs_getarownumnz = self.__obj.getarownumnz_i_2(i)
      if _res_getarownumnz != 0:
        _,_msg_getarownumnz = self.__getlasterror(_res_getarownumnz)
        raise Error(rescode(_res_getarownumnz),_msg_getarownumnz)
      else:
        (nzi) = _retargs_getarownumnz
      return (nzi)
    def getarownumnz(self,*args,**kwds):
      """
      Obtains the number of non-zero elements in one row of the linear constraint matrix
    
      getarownumnz(i) -> (nzi)
        [i : int32]  Index of the row.  
        [nzi : int32]  Number of non-zeros in the i'th row of `A`.  
      """
      return self.__getarownumnz_i_2(*args,**kwds)
    def __getarow_iOO_4(self,i,subi,vali):
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",[0 for _ in range(len(subi))])
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if vali is None:
        raise TypeError("Argument vali may not be None")
      copyback_vali = False
      if vali is None:
        vali_ = None
        memview_vali = None
      else:
        try:
          memview_vali = memoryview(vali)
        except TypeError:
          try:
            _tmparray_vali = array.array("d",[0 for _ in range(len(vali))])
          except TypeError:
            raise TypeError("Argument vali has wrong type") from None
          else:
            memview_vali = memoryview(_tmparray_vali)
            copyback_vali = True
            vali_ = _tmparray_vali
        else:
          if memview_vali.ndim != 1:
            raise TypeError("Argument vali must be one-dimensional")
          if memview_vali.format != "d":
            _tmparray_vali = array.array("d",vali)
            memview_vali = memoryview(_tmparray_vali)
            copyback_vali = True
            vali_ = _tmparray_vali
      _res_getarow,_retargs_getarow = self.__obj.getarow_iOO_4(i,memview_subi,memview_vali)
      if _res_getarow != 0:
        _,_msg_getarow = self.__getlasterror(_res_getarow)
        raise Error(rescode(_res_getarow),_msg_getarow)
      else:
        (nzi) = _retargs_getarow
      if copyback_subi:
        for __tmp_62 in range(len(subi)): subi[__tmp_62] = subi_[__tmp_62]
      if copyback_vali:
        for __tmp_65 in range(len(vali)): vali[__tmp_65] = vali_[__tmp_65]
      return (nzi)
    def __getarow_iOO_2(self,i):
      subi_ = bytearray(0)
      vali_ = bytearray(0)
      _res_getarow,_retargs_getarow = self.__obj.getarow_iOO_2(i,subi_,vali_)
      if _res_getarow != 0:
        _,_msg_getarow = self.__getlasterror(_res_getarow)
        raise Error(rescode(_res_getarow),_msg_getarow)
      else:
        (nzi) = _retargs_getarow
      subi = array.array("i")
      subi.frombytes(subi_)
      vali = array.array("d")
      vali.frombytes(vali_)
      return (nzi,subi,vali)
    def getarow(self,*args,**kwds):
      """
      Obtains one row of the linear constraint matrix.
    
      getarow(i,subi,vali) -> (nzi)
      getarow(i) -> (nzi,subi,vali)
        [i : int32]  Index of the row.  
        [nzi : int32]  Number of non-zeros in the row obtained.  
        [subi : array(int32)]  Column indices of the non-zeros in the row obtained.  
        [vali : array(float64)]  Numerical values of the row obtained.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getarow_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getarow_iOO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getacolslicenumnz64_ii_3(self,first,last):
      _res_getacolslicenumnz64,_retargs_getacolslicenumnz64 = self.__obj.getacolslicenumnz64_ii_3(first,last)
      if _res_getacolslicenumnz64 != 0:
        _,_msg_getacolslicenumnz64 = self.__getlasterror(_res_getacolslicenumnz64)
        raise Error(rescode(_res_getacolslicenumnz64),_msg_getacolslicenumnz64)
      else:
        (numnz) = _retargs_getacolslicenumnz64
      return (numnz)
    def getacolslicenumnz(self,*args,**kwds):
      """
      Obtains the number of non-zeros in a slice of columns of the coefficient matrix.
    
      getacolslicenumnz(first,last) -> (numnz)
        [first : int32]  Index of the first column in the sequence.  
        [last : int32]  Index of the last column plus one in the sequence.  
        [numnz : int64]  Number of non-zeros in the slice.  
      """
      return self.__getacolslicenumnz64_ii_3(*args,**kwds)
    def __getarowslicenumnz64_ii_3(self,first,last):
      _res_getarowslicenumnz64,_retargs_getarowslicenumnz64 = self.__obj.getarowslicenumnz64_ii_3(first,last)
      if _res_getarowslicenumnz64 != 0:
        _,_msg_getarowslicenumnz64 = self.__getlasterror(_res_getarowslicenumnz64)
        raise Error(rescode(_res_getarowslicenumnz64),_msg_getarowslicenumnz64)
      else:
        (numnz) = _retargs_getarowslicenumnz64
      return (numnz)
    def getarowslicenumnz(self,*args,**kwds):
      """
      Obtains the number of non-zeros in a slice of rows of the coefficient matrix.
    
      getarowslicenumnz(first,last) -> (numnz)
        [first : int32]  Index of the first row in the sequence.  
        [last : int32]  Index of the last row plus one in the sequence.  
        [numnz : int64]  Number of non-zeros in the slice.  
      """
      return self.__getarowslicenumnz64_ii_3(*args,**kwds)
    def __getarowslice64_iiOOOO_7(self,first,last,ptrb,ptre,sub,val):
      if ptrb is None:
        raise TypeError("Argument ptrb may not be None")
      copyback_ptrb = False
      if ptrb is None:
        ptrb_ = None
        memview_ptrb = None
      else:
        try:
          memview_ptrb = memoryview(ptrb)
        except TypeError:
          try:
            _tmparray_ptrb = array.array("q",[0 for _ in range(len(ptrb))])
          except TypeError:
            raise TypeError("Argument ptrb has wrong type") from None
          else:
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
        else:
          if memview_ptrb.ndim != 1:
            raise TypeError("Argument ptrb must be one-dimensional")
          if memview_ptrb.format != "q":
            _tmparray_ptrb = array.array("q",ptrb)
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
      if ptre is None:
        raise TypeError("Argument ptre may not be None")
      copyback_ptre = False
      if ptre is None:
        ptre_ = None
        memview_ptre = None
      else:
        try:
          memview_ptre = memoryview(ptre)
        except TypeError:
          try:
            _tmparray_ptre = array.array("q",[0 for _ in range(len(ptre))])
          except TypeError:
            raise TypeError("Argument ptre has wrong type") from None
          else:
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
        else:
          if memview_ptre.ndim != 1:
            raise TypeError("Argument ptre must be one-dimensional")
          if memview_ptre.format != "q":
            _tmparray_ptre = array.array("q",ptre)
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",[0 for _ in range(len(sub))])
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if val is None:
        raise TypeError("Argument val may not be None")
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",[0 for _ in range(len(val))])
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_getarowslice64,_retargs_getarowslice64 = self.__obj.getarowslice64_iiOOOO_7(first,last,memview_ptrb,memview_ptre,memview_sub,memview_val)
      if _res_getarowslice64 != 0:
        _,_msg_getarowslice64 = self.__getlasterror(_res_getarowslice64)
        raise Error(rescode(_res_getarowslice64),_msg_getarowslice64)
      if copyback_ptrb:
        for __tmp_74 in range(len(ptrb)): ptrb[__tmp_74] = ptrb_[__tmp_74]
      if copyback_ptre:
        for __tmp_75 in range(len(ptre)): ptre[__tmp_75] = ptre_[__tmp_75]
      if copyback_sub:
        for __tmp_76 in range(len(sub)): sub[__tmp_76] = sub_[__tmp_76]
      if copyback_val:
        for __tmp_77 in range(len(val)): val[__tmp_77] = val_[__tmp_77]
    def __getarowslice64_iiOOOO_3(self,first,last):
      ptrb_ = bytearray(0)
      ptre_ = bytearray(0)
      sub_ = bytearray(0)
      val_ = bytearray(0)
      _res_getarowslice64,_retargs_getarowslice64 = self.__obj.getarowslice64_iiOOOO_3(first,last,ptrb_,ptre_,sub_,val_)
      if _res_getarowslice64 != 0:
        _,_msg_getarowslice64 = self.__getlasterror(_res_getarowslice64)
        raise Error(rescode(_res_getarowslice64),_msg_getarowslice64)
      ptrb = array.array("q")
      ptrb.frombytes(ptrb_)
      ptre = array.array("q")
      ptre.frombytes(ptre_)
      sub = array.array("i")
      sub.frombytes(sub_)
      val = array.array("d")
      val.frombytes(val_)
      return (ptrb,ptre,sub,val)
    def getarowslice(self,*args,**kwds):
      """
      Obtains a sequence of rows from the coefficient matrix.
    
      getarowslice(first,last,ptrb,ptre,sub,val)
      getarowslice(first,last) -> (ptrb,ptre,sub,val)
        [first : int32]  Index of the first row in the sequence.  
        [last : int32]  Index of the last row in the sequence plus one.  
        [ptrb : array(int64)]  Row start pointers.  
        [ptre : array(int64)]  Row end pointers.  
        [sub : array(int32)]  Contains the column subscripts.  
        [val : array(float64)]  Contains the coefficient values.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 7: return self.__getarowslice64_iiOOOO_7(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getarowslice64_iiOOOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getatrip_OOO_4(self,subi,subj,val):
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",[0 for _ in range(len(subi))])
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",[0 for _ in range(len(subj))])
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",[0 for _ in range(len(val))])
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_getatrip,_retargs_getatrip = self.__obj.getatrip_OOO_4(memview_subi,memview_subj,memview_val)
      if _res_getatrip != 0:
        _,_msg_getatrip = self.__getlasterror(_res_getatrip)
        raise Error(rescode(_res_getatrip),_msg_getatrip)
      if copyback_subi:
        for __tmp_86 in range(len(subi)): subi[__tmp_86] = subi_[__tmp_86]
      if copyback_subj:
        for __tmp_87 in range(len(subj)): subj[__tmp_87] = subj_[__tmp_87]
      if copyback_val:
        for __tmp_88 in range(len(val)): val[__tmp_88] = val_[__tmp_88]
    def __getatrip_OOO_1(self):
      subi_ = bytearray(0)
      subj_ = bytearray(0)
      val_ = bytearray(0)
      _res_getatrip,_retargs_getatrip = self.__obj.getatrip_OOO_1(subi_,subj_,val_)
      if _res_getatrip != 0:
        _,_msg_getatrip = self.__getlasterror(_res_getatrip)
        raise Error(rescode(_res_getatrip),_msg_getatrip)
      subi = array.array("i")
      subi.frombytes(subi_)
      subj = array.array("i")
      subj.frombytes(subj_)
      val = array.array("d")
      val.frombytes(val_)
      return (subi,subj,val)
    def getatrip(self,*args,**kwds):
      """
      Obtains the A matrix in sparse triplet format.
    
      getatrip(subi,subj,val)
      getatrip() -> (subi,subj,val)
        [subi : array(int32)]  Constraint subscripts.  
        [subj : array(int32)]  Column subscripts.  
        [val : array(float64)]  Values.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getatrip_OOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getatrip_OOO_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getarowslicetrip_iiOOO_6(self,first,last,subi,subj,val):
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",[0 for _ in range(len(subi))])
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",[0 for _ in range(len(subj))])
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",[0 for _ in range(len(val))])
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_getarowslicetrip,_retargs_getarowslicetrip = self.__obj.getarowslicetrip_iiOOO_6(first,last,memview_subi,memview_subj,memview_val)
      if _res_getarowslicetrip != 0:
        _,_msg_getarowslicetrip = self.__getlasterror(_res_getarowslicetrip)
        raise Error(rescode(_res_getarowslicetrip),_msg_getarowslicetrip)
      if copyback_subi:
        for __tmp_96 in range(len(subi)): subi[__tmp_96] = subi_[__tmp_96]
      if copyback_subj:
        for __tmp_97 in range(len(subj)): subj[__tmp_97] = subj_[__tmp_97]
      if copyback_val:
        for __tmp_98 in range(len(val)): val[__tmp_98] = val_[__tmp_98]
    def __getarowslicetrip_iiOOO_3(self,first,last):
      subi_ = bytearray(0)
      subj_ = bytearray(0)
      val_ = bytearray(0)
      _res_getarowslicetrip,_retargs_getarowslicetrip = self.__obj.getarowslicetrip_iiOOO_3(first,last,subi_,subj_,val_)
      if _res_getarowslicetrip != 0:
        _,_msg_getarowslicetrip = self.__getlasterror(_res_getarowslicetrip)
        raise Error(rescode(_res_getarowslicetrip),_msg_getarowslicetrip)
      subi = array.array("i")
      subi.frombytes(subi_)
      subj = array.array("i")
      subj.frombytes(subj_)
      val = array.array("d")
      val.frombytes(val_)
      return (subi,subj,val)
    def getarowslicetrip(self,*args,**kwds):
      """
      Obtains a sequence of rows from the coefficient matrix in sparse triplet format.
    
      getarowslicetrip(first,last,subi,subj,val)
      getarowslicetrip(first,last) -> (subi,subj,val)
        [first : int32]  Index of the first row in the sequence.  
        [last : int32]  Index of the last row in the sequence plus one.  
        [subi : array(int32)]  Constraint subscripts.  
        [subj : array(int32)]  Column subscripts.  
        [val : array(float64)]  Values.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__getarowslicetrip_iiOOO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getarowslicetrip_iiOOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getacolslicetrip_iiOOO_6(self,first,last,subi,subj,val):
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",[0 for _ in range(len(subi))])
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",[0 for _ in range(len(subj))])
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",[0 for _ in range(len(val))])
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_getacolslicetrip,_retargs_getacolslicetrip = self.__obj.getacolslicetrip_iiOOO_6(first,last,memview_subi,memview_subj,memview_val)
      if _res_getacolslicetrip != 0:
        _,_msg_getacolslicetrip = self.__getlasterror(_res_getacolslicetrip)
        raise Error(rescode(_res_getacolslicetrip),_msg_getacolslicetrip)
      if copyback_subi:
        for __tmp_106 in range(len(subi)): subi[__tmp_106] = subi_[__tmp_106]
      if copyback_subj:
        for __tmp_107 in range(len(subj)): subj[__tmp_107] = subj_[__tmp_107]
      if copyback_val:
        for __tmp_108 in range(len(val)): val[__tmp_108] = val_[__tmp_108]
    def __getacolslicetrip_iiOOO_3(self,first,last):
      subi_ = bytearray(0)
      subj_ = bytearray(0)
      val_ = bytearray(0)
      _res_getacolslicetrip,_retargs_getacolslicetrip = self.__obj.getacolslicetrip_iiOOO_3(first,last,subi_,subj_,val_)
      if _res_getacolslicetrip != 0:
        _,_msg_getacolslicetrip = self.__getlasterror(_res_getacolslicetrip)
        raise Error(rescode(_res_getacolslicetrip),_msg_getacolslicetrip)
      subi = array.array("i")
      subi.frombytes(subi_)
      subj = array.array("i")
      subj.frombytes(subj_)
      val = array.array("d")
      val.frombytes(val_)
      return (subi,subj,val)
    def getacolslicetrip(self,*args,**kwds):
      """
      Obtains a sequence of columns from the coefficient matrix in triplet format.
    
      getacolslicetrip(first,last,subi,subj,val)
      getacolslicetrip(first,last) -> (subi,subj,val)
        [first : int32]  Index of the first column in the sequence.  
        [last : int32]  Index of the last column in the sequence plus one.  
        [subi : array(int32)]  Constraint subscripts.  
        [subj : array(int32)]  Column subscripts.  
        [val : array(float64)]  Values.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__getacolslicetrip_iiOOO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getacolslicetrip_iiOOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getconbound_i_2(self,i):
      _res_getconbound,_retargs_getconbound = self.__obj.getconbound_i_2(i)
      if _res_getconbound != 0:
        _,_msg_getconbound = self.__getlasterror(_res_getconbound)
        raise Error(rescode(_res_getconbound),_msg_getconbound)
      else:
        (bk,bl,bu) = _retargs_getconbound
      return (boundkey(bk),bl,bu)
    def getconbound(self,*args,**kwds):
      """
      Obtains bound information for one constraint.
    
      getconbound(i) -> (bk,bl,bu)
        [bk : mosek.boundkey]  Bound keys.  
        [bl : float64]  Values for lower bounds.  
        [bu : float64]  Values for upper bounds.  
        [i : int32]  Index of the constraint for which the bound information should be obtained.  
      """
      return self.__getconbound_i_2(*args,**kwds)
    def __getvarbound_i_2(self,i):
      _res_getvarbound,_retargs_getvarbound = self.__obj.getvarbound_i_2(i)
      if _res_getvarbound != 0:
        _,_msg_getvarbound = self.__getlasterror(_res_getvarbound)
        raise Error(rescode(_res_getvarbound),_msg_getvarbound)
      else:
        (bk,bl,bu) = _retargs_getvarbound
      return (boundkey(bk),bl,bu)
    def getvarbound(self,*args,**kwds):
      """
      Obtains bound information for one variable.
    
      getvarbound(i) -> (bk,bl,bu)
        [bk : mosek.boundkey]  Bound keys.  
        [bl : float64]  Values for lower bounds.  
        [bu : float64]  Values for upper bounds.  
        [i : int32]  Index of the variable for which the bound information should be obtained.  
      """
      return self.__getvarbound_i_2(*args,**kwds)
    def __getconboundslice_iiOOO_6(self,first,last,bk,bl,bu):
      if bk is None:
        bk_ = None
      else:
        # o
        _tmparray_bk_ = array.array("i",[0 for _ in range(len(bk))])
        bk_ = memoryview(_tmparray_bk_)
      copyback_bl = False
      if bl is None:
        bl_ = None
        memview_bl = None
      else:
        try:
          memview_bl = memoryview(bl)
        except TypeError:
          try:
            _tmparray_bl = array.array("d",[0 for _ in range(len(bl))])
          except TypeError:
            raise TypeError("Argument bl has wrong type") from None
          else:
            memview_bl = memoryview(_tmparray_bl)
            copyback_bl = True
            bl_ = _tmparray_bl
        else:
          if memview_bl.ndim != 1:
            raise TypeError("Argument bl must be one-dimensional")
          if memview_bl.format != "d":
            _tmparray_bl = array.array("d",bl)
            memview_bl = memoryview(_tmparray_bl)
            copyback_bl = True
            bl_ = _tmparray_bl
      copyback_bu = False
      if bu is None:
        bu_ = None
        memview_bu = None
      else:
        try:
          memview_bu = memoryview(bu)
        except TypeError:
          try:
            _tmparray_bu = array.array("d",[0 for _ in range(len(bu))])
          except TypeError:
            raise TypeError("Argument bu has wrong type") from None
          else:
            memview_bu = memoryview(_tmparray_bu)
            copyback_bu = True
            bu_ = _tmparray_bu
        else:
          if memview_bu.ndim != 1:
            raise TypeError("Argument bu must be one-dimensional")
          if memview_bu.format != "d":
            _tmparray_bu = array.array("d",bu)
            memview_bu = memoryview(_tmparray_bu)
            copyback_bu = True
            bu_ = _tmparray_bu
      _res_getconboundslice,_retargs_getconboundslice = self.__obj.getconboundslice_iiOOO_6(first,last,bk_,memview_bl,memview_bu)
      if _res_getconboundslice != 0:
        _,_msg_getconboundslice = self.__getlasterror(_res_getconboundslice)
        raise Error(rescode(_res_getconboundslice),_msg_getconboundslice)
      for __tmp_114 in range(len(bk)): bk[__tmp_114] = boundkey(bk_[__tmp_114])
      if copyback_bl:
        for __tmp_115 in range(len(bl)): bl[__tmp_115] = bl_[__tmp_115]
      if copyback_bu:
        for __tmp_116 in range(len(bu)): bu[__tmp_116] = bu_[__tmp_116]
    def __getconboundslice_iiOOO_3(self,first,last):
      bk_ = bytearray(0)
      bl_ = bytearray(0)
      bu_ = bytearray(0)
      _res_getconboundslice,_retargs_getconboundslice = self.__obj.getconboundslice_iiOOO_3(first,last,bk_,bl_,bu_)
      if _res_getconboundslice != 0:
        _,_msg_getconboundslice = self.__getlasterror(_res_getconboundslice)
        raise Error(rescode(_res_getconboundslice),_msg_getconboundslice)
      bk_ints = array.array("i")
      bk_ints.frombytes(bk_)
      bk = [ boundkey(__tmp_117) for __tmp_117 in bk_ints ]
      bl = array.array("d")
      bl.frombytes(bl_)
      bu = array.array("d")
      bu.frombytes(bu_)
      return (bk,bl,bu)
    def getconboundslice(self,*args,**kwds):
      """
      Obtains bounds information for a slice of the constraints.
    
      getconboundslice(first,last,bk,bl,bu)
      getconboundslice(first,last) -> (bk,bl,bu)
        [bk : array(mosek.boundkey)]  Bound keys.  
        [bl : array(float64)]  Values for lower bounds.  
        [bu : array(float64)]  Values for upper bounds.  
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__getconboundslice_iiOOO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getconboundslice_iiOOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getvarboundslice_iiOOO_6(self,first,last,bk,bl,bu):
      if bk is None:
        bk_ = None
      else:
        # o
        _tmparray_bk_ = array.array("i",[0 for _ in range(len(bk))])
        bk_ = memoryview(_tmparray_bk_)
      copyback_bl = False
      if bl is None:
        bl_ = None
        memview_bl = None
      else:
        try:
          memview_bl = memoryview(bl)
        except TypeError:
          try:
            _tmparray_bl = array.array("d",[0 for _ in range(len(bl))])
          except TypeError:
            raise TypeError("Argument bl has wrong type") from None
          else:
            memview_bl = memoryview(_tmparray_bl)
            copyback_bl = True
            bl_ = _tmparray_bl
        else:
          if memview_bl.ndim != 1:
            raise TypeError("Argument bl must be one-dimensional")
          if memview_bl.format != "d":
            _tmparray_bl = array.array("d",bl)
            memview_bl = memoryview(_tmparray_bl)
            copyback_bl = True
            bl_ = _tmparray_bl
      copyback_bu = False
      if bu is None:
        bu_ = None
        memview_bu = None
      else:
        try:
          memview_bu = memoryview(bu)
        except TypeError:
          try:
            _tmparray_bu = array.array("d",[0 for _ in range(len(bu))])
          except TypeError:
            raise TypeError("Argument bu has wrong type") from None
          else:
            memview_bu = memoryview(_tmparray_bu)
            copyback_bu = True
            bu_ = _tmparray_bu
        else:
          if memview_bu.ndim != 1:
            raise TypeError("Argument bu must be one-dimensional")
          if memview_bu.format != "d":
            _tmparray_bu = array.array("d",bu)
            memview_bu = memoryview(_tmparray_bu)
            copyback_bu = True
            bu_ = _tmparray_bu
      _res_getvarboundslice,_retargs_getvarboundslice = self.__obj.getvarboundslice_iiOOO_6(first,last,bk_,memview_bl,memview_bu)
      if _res_getvarboundslice != 0:
        _,_msg_getvarboundslice = self.__getlasterror(_res_getvarboundslice)
        raise Error(rescode(_res_getvarboundslice),_msg_getvarboundslice)
      for __tmp_120 in range(len(bk)): bk[__tmp_120] = boundkey(bk_[__tmp_120])
      if copyback_bl:
        for __tmp_121 in range(len(bl)): bl[__tmp_121] = bl_[__tmp_121]
      if copyback_bu:
        for __tmp_122 in range(len(bu)): bu[__tmp_122] = bu_[__tmp_122]
    def __getvarboundslice_iiOOO_3(self,first,last):
      bk_ = bytearray(0)
      bl_ = bytearray(0)
      bu_ = bytearray(0)
      _res_getvarboundslice,_retargs_getvarboundslice = self.__obj.getvarboundslice_iiOOO_3(first,last,bk_,bl_,bu_)
      if _res_getvarboundslice != 0:
        _,_msg_getvarboundslice = self.__getlasterror(_res_getvarboundslice)
        raise Error(rescode(_res_getvarboundslice),_msg_getvarboundslice)
      bk_ints = array.array("i")
      bk_ints.frombytes(bk_)
      bk = [ boundkey(__tmp_123) for __tmp_123 in bk_ints ]
      bl = array.array("d")
      bl.frombytes(bl_)
      bu = array.array("d")
      bu.frombytes(bu_)
      return (bk,bl,bu)
    def getvarboundslice(self,*args,**kwds):
      """
      Obtains bounds information for a slice of the variables.
    
      getvarboundslice(first,last,bk,bl,bu)
      getvarboundslice(first,last) -> (bk,bl,bu)
        [bk : array(mosek.boundkey)]  Bound keys.  
        [bl : array(float64)]  Values for lower bounds.  
        [bu : array(float64)]  Values for upper bounds.  
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__getvarboundslice_iiOOO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getvarboundslice_iiOOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getcj_i_2(self,j):
      _res_getcj,_retargs_getcj = self.__obj.getcj_i_2(j)
      if _res_getcj != 0:
        _,_msg_getcj = self.__getlasterror(_res_getcj)
        raise Error(rescode(_res_getcj),_msg_getcj)
      else:
        (cj) = _retargs_getcj
      return (cj)
    def getcj(self,*args,**kwds):
      """
      Obtains one objective coefficient.
    
      getcj(j) -> (cj)
        [cj : float64]  The c coefficient value.  
        [j : int32]  Index of the variable for which the c coefficient should be obtained.  
      """
      return self.__getcj_i_2(*args,**kwds)
    def __getc_O_2(self,c):
      copyback_c = False
      if c is None:
        c_ = None
        memview_c = None
      else:
        try:
          memview_c = memoryview(c)
        except TypeError:
          try:
            _tmparray_c = array.array("d",[0 for _ in range(len(c))])
          except TypeError:
            raise TypeError("Argument c has wrong type") from None
          else:
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
        else:
          if memview_c.ndim != 1:
            raise TypeError("Argument c must be one-dimensional")
          if memview_c.format != "d":
            _tmparray_c = array.array("d",c)
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
      _res_getc,_retargs_getc = self.__obj.getc_O_2(memview_c)
      if _res_getc != 0:
        _,_msg_getc = self.__getlasterror(_res_getc)
        raise Error(rescode(_res_getc),_msg_getc)
      if copyback_c:
        for __tmp_128 in range(len(c)): c[__tmp_128] = c_[__tmp_128]
    def __getc_O_1(self):
      c_ = bytearray(0)
      _res_getc,_retargs_getc = self.__obj.getc_O_1(c_)
      if _res_getc != 0:
        _,_msg_getc = self.__getlasterror(_res_getc)
        raise Error(rescode(_res_getc),_msg_getc)
      c = array.array("d")
      c.frombytes(c_)
      return (c)
    def getc(self,*args,**kwds):
      """
      Obtains all objective coefficients.
    
      getc(c)
      getc() -> (c)
        [c : array(float64)]  Linear terms of the objective as a dense vector. The length is the number of variables.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 2: return self.__getc_O_2(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getc_O_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getcfix__1(self):
      _res_getcfix,_retargs_getcfix = self.__obj.getcfix__1()
      if _res_getcfix != 0:
        _,_msg_getcfix = self.__getlasterror(_res_getcfix)
        raise Error(rescode(_res_getcfix),_msg_getcfix)
      else:
        (cfix) = _retargs_getcfix
      return (cfix)
    def getcfix(self,*args,**kwds):
      """
      Obtains the fixed term in the objective.
    
      getcfix() -> (cfix)
        [cfix : float64]  Fixed term in the objective.  
      """
      return self.__getcfix__1(*args,**kwds)
    def __getcone_iO_3(self,k,submem):
      copyback_submem = False
      if submem is None:
        submem_ = None
        memview_submem = None
      else:
        try:
          memview_submem = memoryview(submem)
        except TypeError:
          try:
            _tmparray_submem = array.array("i",[0 for _ in range(len(submem))])
          except TypeError:
            raise TypeError("Argument submem has wrong type") from None
          else:
            memview_submem = memoryview(_tmparray_submem)
            copyback_submem = True
            submem_ = _tmparray_submem
        else:
          if memview_submem.ndim != 1:
            raise TypeError("Argument submem must be one-dimensional")
          if memview_submem.format != "i":
            _tmparray_submem = array.array("i",submem)
            memview_submem = memoryview(_tmparray_submem)
            copyback_submem = True
            submem_ = _tmparray_submem
      _res_getcone,_retargs_getcone = self.__obj.getcone_iO_3(k,memview_submem)
      if _res_getcone != 0:
        _,_msg_getcone = self.__getlasterror(_res_getcone)
        raise Error(rescode(_res_getcone),_msg_getcone)
      else:
        (ct,conepar,nummem) = _retargs_getcone
      if copyback_submem:
        for __tmp_136 in range(len(submem)): submem[__tmp_136] = submem_[__tmp_136]
      return (conetype(ct),conepar,nummem)
    def __getcone_iO_2(self,k):
      submem_ = bytearray(0)
      _res_getcone,_retargs_getcone = self.__obj.getcone_iO_2(k,submem_)
      if _res_getcone != 0:
        _,_msg_getcone = self.__getlasterror(_res_getcone)
        raise Error(rescode(_res_getcone),_msg_getcone)
      else:
        (ct,conepar,nummem) = _retargs_getcone
      submem = array.array("i")
      submem.frombytes(submem_)
      return (conetype(ct),conepar,nummem,submem)
    def getcone(self,*args,**kwds):
      """
      Obtains a cone.
    
      getcone(k,submem) -> (ct,conepar,nummem)
      getcone(k) -> (ct,conepar,nummem,submem)
        [conepar : float64]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
        [ct : mosek.conetype]  Specifies the type of the cone.  
        [k : int32]  Index of the cone.  
        [nummem : int32]  Number of member variables in the cone.  
        [submem : array(int32)]  Variable subscripts of the members in the cone.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getcone_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getcone_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getconeinfo_i_2(self,k):
      _res_getconeinfo,_retargs_getconeinfo = self.__obj.getconeinfo_i_2(k)
      if _res_getconeinfo != 0:
        _,_msg_getconeinfo = self.__getlasterror(_res_getconeinfo)
        raise Error(rescode(_res_getconeinfo),_msg_getconeinfo)
      else:
        (ct,conepar,nummem) = _retargs_getconeinfo
      return (conetype(ct),conepar,nummem)
    def getconeinfo(self,*args,**kwds):
      """
      Obtains information about a cone.
    
      getconeinfo(k) -> (ct,conepar,nummem)
        [conepar : float64]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
        [ct : mosek.conetype]  Specifies the type of the cone.  
        [k : int32]  Index of the cone.  
        [nummem : int32]  Number of member variables in the cone.  
      """
      return self.__getconeinfo_i_2(*args,**kwds)
    def __getclist_OO_3(self,subj,c):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if c is None:
        raise TypeError("Argument c may not be None")
      copyback_c = False
      if c is None:
        c_ = None
        memview_c = None
      else:
        try:
          memview_c = memoryview(c)
        except TypeError:
          try:
            _tmparray_c = array.array("d",[0 for _ in range(len(c))])
          except TypeError:
            raise TypeError("Argument c has wrong type") from None
          else:
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
        else:
          if memview_c.ndim != 1:
            raise TypeError("Argument c must be one-dimensional")
          if memview_c.format != "d":
            _tmparray_c = array.array("d",c)
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
      _res_getclist,_retargs_getclist = self.__obj.getclist_OO_3(memview_subj,memview_c)
      if _res_getclist != 0:
        _,_msg_getclist = self.__getlasterror(_res_getclist)
        raise Error(rescode(_res_getclist),_msg_getclist)
      if copyback_c:
        for __tmp_143 in range(len(c)): c[__tmp_143] = c_[__tmp_143]
    def __getclist_OO_2(self,subj):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      c_ = bytearray(0)
      _res_getclist,_retargs_getclist = self.__obj.getclist_OO_2(memview_subj,c_)
      if _res_getclist != 0:
        _,_msg_getclist = self.__getlasterror(_res_getclist)
        raise Error(rescode(_res_getclist),_msg_getclist)
      c = array.array("d")
      c.frombytes(c_)
      return (c)
    def getclist(self,*args,**kwds):
      """
      Obtains a sequence of coefficients from the objective.
    
      getclist(subj,c)
      getclist(subj) -> (c)
        [c : array(float64)]  Linear terms of the requested list of the objective as a dense vector.  
        [subj : array(int32)]  A list of variable indexes.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getclist_OO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getclist_OO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getcslice_iiO_4(self,first,last,c):
      copyback_c = False
      if c is None:
        c_ = None
        memview_c = None
      else:
        try:
          memview_c = memoryview(c)
        except TypeError:
          try:
            _tmparray_c = array.array("d",[0 for _ in range(len(c))])
          except TypeError:
            raise TypeError("Argument c has wrong type") from None
          else:
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
        else:
          if memview_c.ndim != 1:
            raise TypeError("Argument c must be one-dimensional")
          if memview_c.format != "d":
            _tmparray_c = array.array("d",c)
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
      _res_getcslice,_retargs_getcslice = self.__obj.getcslice_iiO_4(first,last,memview_c)
      if _res_getcslice != 0:
        _,_msg_getcslice = self.__getlasterror(_res_getcslice)
        raise Error(rescode(_res_getcslice),_msg_getcslice)
      if copyback_c:
        for __tmp_146 in range(len(c)): c[__tmp_146] = c_[__tmp_146]
    def __getcslice_iiO_3(self,first,last):
      c_ = bytearray(0)
      _res_getcslice,_retargs_getcslice = self.__obj.getcslice_iiO_3(first,last,c_)
      if _res_getcslice != 0:
        _,_msg_getcslice = self.__getlasterror(_res_getcslice)
        raise Error(rescode(_res_getcslice),_msg_getcslice)
      c = array.array("d")
      c.frombytes(c_)
      return (c)
    def getcslice(self,*args,**kwds):
      """
      Obtains a sequence of coefficients from the objective.
    
      getcslice(first,last,c)
      getcslice(first,last) -> (c)
        [c : array(float64)]  Linear terms of the requested slice of the objective as a dense vector.  
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getcslice_iiO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getcslice_iiO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getdouinf_i_2(self,whichdinf):
      _res_getdouinf,_retargs_getdouinf = self.__obj.getdouinf_i_2(whichdinf)
      if _res_getdouinf != 0:
        _,_msg_getdouinf = self.__getlasterror(_res_getdouinf)
        raise Error(rescode(_res_getdouinf),_msg_getdouinf)
      else:
        (dvalue) = _retargs_getdouinf
      return (dvalue)
    def getdouinf(self,*args,**kwds):
      """
      Obtains a double information item.
    
      getdouinf(whichdinf) -> (dvalue)
        [dvalue : float64]  The value of the required double information item.  
        [whichdinf : mosek.dinfitem]  Specifies a double information item.  
      """
      return self.__getdouinf_i_2(*args,**kwds)
    def __getdouparam_i_2(self,param):
      _res_getdouparam,_retargs_getdouparam = self.__obj.getdouparam_i_2(param)
      if _res_getdouparam != 0:
        _,_msg_getdouparam = self.__getlasterror(_res_getdouparam)
        raise Error(rescode(_res_getdouparam),_msg_getdouparam)
      else:
        (parvalue) = _retargs_getdouparam
      return (parvalue)
    def getdouparam(self,*args,**kwds):
      """
      Obtains a double parameter.
    
      getdouparam(param) -> (parvalue)
        [param : mosek.dparam]  Which parameter.  
        [parvalue : float64]  Parameter value.  
      """
      return self.__getdouparam_i_2(*args,**kwds)
    def __getdualobj_i_2(self,whichsol):
      _res_getdualobj,_retargs_getdualobj = self.__obj.getdualobj_i_2(whichsol)
      if _res_getdualobj != 0:
        _,_msg_getdualobj = self.__getlasterror(_res_getdualobj)
        raise Error(rescode(_res_getdualobj),_msg_getdualobj)
      else:
        (dualobj) = _retargs_getdualobj
      return (dualobj)
    def getdualobj(self,*args,**kwds):
      """
      Computes the dual objective value associated with the solution.
    
      getdualobj(whichsol) -> (dualobj)
        [dualobj : float64]  Objective value corresponding to the dual solution.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__getdualobj_i_2(*args,**kwds)
    def __getintinf_i_2(self,whichiinf):
      _res_getintinf,_retargs_getintinf = self.__obj.getintinf_i_2(whichiinf)
      if _res_getintinf != 0:
        _,_msg_getintinf = self.__getlasterror(_res_getintinf)
        raise Error(rescode(_res_getintinf),_msg_getintinf)
      else:
        (ivalue) = _retargs_getintinf
      return (ivalue)
    def getintinf(self,*args,**kwds):
      """
      Obtains an integer information item.
    
      getintinf(whichiinf) -> (ivalue)
        [ivalue : int32]  The value of the required integer information item.  
        [whichiinf : mosek.iinfitem]  Specifies an integer information item.  
      """
      return self.__getintinf_i_2(*args,**kwds)
    def __getlintinf_i_2(self,whichliinf):
      _res_getlintinf,_retargs_getlintinf = self.__obj.getlintinf_i_2(whichliinf)
      if _res_getlintinf != 0:
        _,_msg_getlintinf = self.__getlasterror(_res_getlintinf)
        raise Error(rescode(_res_getlintinf),_msg_getlintinf)
      else:
        (ivalue) = _retargs_getlintinf
      return (ivalue)
    def getlintinf(self,*args,**kwds):
      """
      Obtains a long integer information item.
    
      getlintinf(whichliinf) -> (ivalue)
        [ivalue : int64]  The value of the required long integer information item.  
        [whichliinf : mosek.liinfitem]  Specifies a long information item.  
      """
      return self.__getlintinf_i_2(*args,**kwds)
    def __getintparam_i_2(self,param):
      _res_getintparam,_retargs_getintparam = self.__obj.getintparam_i_2(param)
      if _res_getintparam != 0:
        _,_msg_getintparam = self.__getlasterror(_res_getintparam)
        raise Error(rescode(_res_getintparam),_msg_getintparam)
      else:
        (parvalue) = _retargs_getintparam
      return (parvalue)
    def getintparam(self,*args,**kwds):
      """
      Obtains an integer parameter.
    
      getintparam(param) -> (parvalue)
        [param : mosek.iparam]  Which parameter.  
        [parvalue : int32]  Parameter value.  
      """
      return self.__getintparam_i_2(*args,**kwds)
    def __getmaxnumanz64__1(self):
      _res_getmaxnumanz64,_retargs_getmaxnumanz64 = self.__obj.getmaxnumanz64__1()
      if _res_getmaxnumanz64 != 0:
        _,_msg_getmaxnumanz64 = self.__getlasterror(_res_getmaxnumanz64)
        raise Error(rescode(_res_getmaxnumanz64),_msg_getmaxnumanz64)
      else:
        (maxnumanz) = _retargs_getmaxnumanz64
      return (maxnumanz)
    def getmaxnumanz(self,*args,**kwds):
      """
      Obtains number of preallocated non-zeros in the linear constraint matrix.
    
      getmaxnumanz() -> (maxnumanz)
        [maxnumanz : int64]  Number of preallocated non-zero linear matrix elements.  
      """
      return self.__getmaxnumanz64__1(*args,**kwds)
    def __getmaxnumcon__1(self):
      _res_getmaxnumcon,_retargs_getmaxnumcon = self.__obj.getmaxnumcon__1()
      if _res_getmaxnumcon != 0:
        _,_msg_getmaxnumcon = self.__getlasterror(_res_getmaxnumcon)
        raise Error(rescode(_res_getmaxnumcon),_msg_getmaxnumcon)
      else:
        (maxnumcon) = _retargs_getmaxnumcon
      return (maxnumcon)
    def getmaxnumcon(self,*args,**kwds):
      """
      Obtains the number of preallocated constraints in the optimization task.
    
      getmaxnumcon() -> (maxnumcon)
        [maxnumcon : int32]  Number of preallocated constraints in the optimization task.  
      """
      return self.__getmaxnumcon__1(*args,**kwds)
    def __getmaxnumvar__1(self):
      _res_getmaxnumvar,_retargs_getmaxnumvar = self.__obj.getmaxnumvar__1()
      if _res_getmaxnumvar != 0:
        _,_msg_getmaxnumvar = self.__getlasterror(_res_getmaxnumvar)
        raise Error(rescode(_res_getmaxnumvar),_msg_getmaxnumvar)
      else:
        (maxnumvar) = _retargs_getmaxnumvar
      return (maxnumvar)
    def getmaxnumvar(self,*args,**kwds):
      """
      Obtains the maximum number variables allowed.
    
      getmaxnumvar() -> (maxnumvar)
        [maxnumvar : int32]  Number of preallocated variables in the optimization task.  
      """
      return self.__getmaxnumvar__1(*args,**kwds)
    def __getbarvarnamelen_i_2(self,i):
      _res_getbarvarnamelen,_retargs_getbarvarnamelen = self.__obj.getbarvarnamelen_i_2(i)
      if _res_getbarvarnamelen != 0:
        _,_msg_getbarvarnamelen = self.__getlasterror(_res_getbarvarnamelen)
        raise Error(rescode(_res_getbarvarnamelen),_msg_getbarvarnamelen)
      else:
        (len) = _retargs_getbarvarnamelen
      return (len)
    def getbarvarnamelen(self,*args,**kwds):
      """
      Obtains the length of the name of a semidefinite variable.
    
      getbarvarnamelen(i) -> (len)
        [i : int32]  Index of the variable.  
        [len : int32]  Returns the length of the indicated name.  
      """
      return self.__getbarvarnamelen_i_2(*args,**kwds)
    def __getbarvarname_iO_2(self,i):
      name = bytearray(0)
      _res_getbarvarname,_retargs_getbarvarname = self.__obj.getbarvarname_iO_2(i,name)
      if _res_getbarvarname != 0:
        _,_msg_getbarvarname = self.__getlasterror(_res_getbarvarname)
        raise Error(rescode(_res_getbarvarname),_msg_getbarvarname)
      __tmp_150 = name.find(b"\0")
      if __tmp_150 >= 0:
        name = name[:__tmp_150]
      return (name.decode("utf-8",errors="ignore"))
    def getbarvarname(self,*args,**kwds):
      """
      Obtains the name of a semidefinite variable.
    
      getbarvarname(i) -> (name)
        [i : int32]  Index of the variable.  
        [name : str]  The requested name is copied to this buffer.  
      """
      return self.__getbarvarname_iO_2(*args,**kwds)
    def __getbarvarnameindex_s_2(self,somename):
      _res_getbarvarnameindex,_retargs_getbarvarnameindex = self.__obj.getbarvarnameindex_s_2(somename)
      if _res_getbarvarnameindex != 0:
        _,_msg_getbarvarnameindex = self.__getlasterror(_res_getbarvarnameindex)
        raise Error(rescode(_res_getbarvarnameindex),_msg_getbarvarnameindex)
      else:
        (asgn,index) = _retargs_getbarvarnameindex
      return (asgn,index)
    def getbarvarnameindex(self,*args,**kwds):
      """
      Obtains the index of semidefinite variable from its name.
    
      getbarvarnameindex(somename) -> (asgn,index)
        [asgn : int32]  Non-zero if the name somename is assigned to some semidefinite variable.  
        [index : int32]  The index of a semidefinite variable with the name somename (if one exists).  
        [somename : str]  The name of the variable.  
      """
      return self.__getbarvarnameindex_s_2(*args,**kwds)
    def __generatebarvarnames_OsOOOOO_7(self,subj,fmt,dims,sp,namedaxisidxs,names):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if dims is None:
        raise TypeError("Argument dims may not be None")
      copyback_dims = False
      if dims is None:
        dims_ = None
        memview_dims = None
      else:
        try:
          memview_dims = memoryview(dims)
        except TypeError:
          try:
            _tmparray_dims = array.array("i",dims)
          except TypeError:
            raise TypeError("Argument dims has wrong type") from None
          else:
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
        else:
          if memview_dims.ndim != 1:
            raise TypeError("Argument dims must be one-dimensional")
          if memview_dims.format != "i":
            _tmparray_dims = array.array("i",dims)
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
      copyback_sp = False
      if sp is None:
        sp_ = None
        memview_sp = None
      else:
        try:
          memview_sp = memoryview(sp)
        except TypeError:
          try:
            _tmparray_sp = array.array("q",sp)
          except TypeError:
            raise TypeError("Argument sp has wrong type") from None
          else:
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
        else:
          if memview_sp.ndim != 1:
            raise TypeError("Argument sp must be one-dimensional")
          if memview_sp.format != "q":
            _tmparray_sp = array.array("q",sp)
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
      copyback_namedaxisidxs = False
      if namedaxisidxs is None:
        namedaxisidxs_ = None
        memview_namedaxisidxs = None
      else:
        try:
          memview_namedaxisidxs = memoryview(namedaxisidxs)
        except TypeError:
          try:
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
          except TypeError:
            raise TypeError("Argument namedaxisidxs has wrong type") from None
          else:
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
        else:
          if memview_namedaxisidxs.ndim != 1:
            raise TypeError("Argument namedaxisidxs must be one-dimensional")
          if memview_namedaxisidxs.format != "i":
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
      if names is not None:
        __tmp_158 = array.array("q")
        __tmp_159 = bytearray()
        for __tmp_160 in names:
          __tmp_158.append(len(__tmp_159))
          __tmp_159.extend(__tmp_160.encode("utf-8"))
          __tmp_159.append(0)
        __tmp_158.append(len(__tmp_159))
        __tmp_158.pop()
        memview___tmp_158   = memoryview(__tmp_158)
        memview___tmp_159 = memoryview(__tmp_159)
      else:
        memview___tmp_158   = None
        memview___tmp_159 = None
      _res_generatebarvarnames,_retargs_generatebarvarnames = self.__obj.generatebarvarnames_OsOOOOO_7(memview_subj,fmt,memview_dims,memview_sp,memview_namedaxisidxs,memview___tmp_158,memview___tmp_159)
      if _res_generatebarvarnames != 0:
        _,_msg_generatebarvarnames = self.__getlasterror(_res_generatebarvarnames)
        raise Error(rescode(_res_generatebarvarnames),_msg_generatebarvarnames)
    def generatebarvarnames(self,*args,**kwds):
      """
      Generates systematic names for variables.
    
      generatebarvarnames(subj,fmt,dims,sp,namedaxisidxs,names)
        [dims : array(int32)]  Dimensions in the shape.  
        [fmt : str]  The variable name formatting string.  
        [namedaxisidxs : array(int32)]  List if named index axes  
        [names : array(string)]  All axis names.  
        [sp : array(int64)]  Items that should be named.  
        [subj : array(int32)]  Indexes of the variables.  
      """
      return self.__generatebarvarnames_OsOOOOO_7(*args,**kwds)
    def __generatevarnames_OsOOOOO_7(self,subj,fmt,dims,sp,namedaxisidxs,names):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if dims is None:
        raise TypeError("Argument dims may not be None")
      copyback_dims = False
      if dims is None:
        dims_ = None
        memview_dims = None
      else:
        try:
          memview_dims = memoryview(dims)
        except TypeError:
          try:
            _tmparray_dims = array.array("i",dims)
          except TypeError:
            raise TypeError("Argument dims has wrong type") from None
          else:
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
        else:
          if memview_dims.ndim != 1:
            raise TypeError("Argument dims must be one-dimensional")
          if memview_dims.format != "i":
            _tmparray_dims = array.array("i",dims)
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
      copyback_sp = False
      if sp is None:
        sp_ = None
        memview_sp = None
      else:
        try:
          memview_sp = memoryview(sp)
        except TypeError:
          try:
            _tmparray_sp = array.array("q",sp)
          except TypeError:
            raise TypeError("Argument sp has wrong type") from None
          else:
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
        else:
          if memview_sp.ndim != 1:
            raise TypeError("Argument sp must be one-dimensional")
          if memview_sp.format != "q":
            _tmparray_sp = array.array("q",sp)
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
      copyback_namedaxisidxs = False
      if namedaxisidxs is None:
        namedaxisidxs_ = None
        memview_namedaxisidxs = None
      else:
        try:
          memview_namedaxisidxs = memoryview(namedaxisidxs)
        except TypeError:
          try:
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
          except TypeError:
            raise TypeError("Argument namedaxisidxs has wrong type") from None
          else:
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
        else:
          if memview_namedaxisidxs.ndim != 1:
            raise TypeError("Argument namedaxisidxs must be one-dimensional")
          if memview_namedaxisidxs.format != "i":
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
      if names is not None:
        __tmp_178 = array.array("q")
        __tmp_179 = bytearray()
        for __tmp_180 in names:
          __tmp_178.append(len(__tmp_179))
          __tmp_179.extend(__tmp_180.encode("utf-8"))
          __tmp_179.append(0)
        __tmp_178.append(len(__tmp_179))
        __tmp_178.pop()
        memview___tmp_178   = memoryview(__tmp_178)
        memview___tmp_179 = memoryview(__tmp_179)
      else:
        memview___tmp_178   = None
        memview___tmp_179 = None
      _res_generatevarnames,_retargs_generatevarnames = self.__obj.generatevarnames_OsOOOOO_7(memview_subj,fmt,memview_dims,memview_sp,memview_namedaxisidxs,memview___tmp_178,memview___tmp_179)
      if _res_generatevarnames != 0:
        _,_msg_generatevarnames = self.__getlasterror(_res_generatevarnames)
        raise Error(rescode(_res_generatevarnames),_msg_generatevarnames)
    def generatevarnames(self,*args,**kwds):
      """
      Generates systematic names for variables.
    
      generatevarnames(subj,fmt,dims,sp,namedaxisidxs,names)
        [dims : array(int32)]  Dimensions in the shape.  
        [fmt : str]  The variable name formatting string.  
        [namedaxisidxs : array(int32)]  List if named index axes  
        [names : array(string)]  All axis names.  
        [sp : array(int64)]  Items that should be named.  
        [subj : array(int32)]  Indexes of the variables.  
      """
      return self.__generatevarnames_OsOOOOO_7(*args,**kwds)
    def __generateconnames_OsOOOOO_7(self,subi,fmt,dims,sp,namedaxisidxs,names):
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",subi)
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if dims is None:
        raise TypeError("Argument dims may not be None")
      copyback_dims = False
      if dims is None:
        dims_ = None
        memview_dims = None
      else:
        try:
          memview_dims = memoryview(dims)
        except TypeError:
          try:
            _tmparray_dims = array.array("i",dims)
          except TypeError:
            raise TypeError("Argument dims has wrong type") from None
          else:
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
        else:
          if memview_dims.ndim != 1:
            raise TypeError("Argument dims must be one-dimensional")
          if memview_dims.format != "i":
            _tmparray_dims = array.array("i",dims)
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
      copyback_sp = False
      if sp is None:
        sp_ = None
        memview_sp = None
      else:
        try:
          memview_sp = memoryview(sp)
        except TypeError:
          try:
            _tmparray_sp = array.array("q",sp)
          except TypeError:
            raise TypeError("Argument sp has wrong type") from None
          else:
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
        else:
          if memview_sp.ndim != 1:
            raise TypeError("Argument sp must be one-dimensional")
          if memview_sp.format != "q":
            _tmparray_sp = array.array("q",sp)
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
      copyback_namedaxisidxs = False
      if namedaxisidxs is None:
        namedaxisidxs_ = None
        memview_namedaxisidxs = None
      else:
        try:
          memview_namedaxisidxs = memoryview(namedaxisidxs)
        except TypeError:
          try:
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
          except TypeError:
            raise TypeError("Argument namedaxisidxs has wrong type") from None
          else:
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
        else:
          if memview_namedaxisidxs.ndim != 1:
            raise TypeError("Argument namedaxisidxs must be one-dimensional")
          if memview_namedaxisidxs.format != "i":
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
      if names is not None:
        __tmp_198 = array.array("q")
        __tmp_199 = bytearray()
        for __tmp_200 in names:
          __tmp_198.append(len(__tmp_199))
          __tmp_199.extend(__tmp_200.encode("utf-8"))
          __tmp_199.append(0)
        __tmp_198.append(len(__tmp_199))
        __tmp_198.pop()
        memview___tmp_198   = memoryview(__tmp_198)
        memview___tmp_199 = memoryview(__tmp_199)
      else:
        memview___tmp_198   = None
        memview___tmp_199 = None
      _res_generateconnames,_retargs_generateconnames = self.__obj.generateconnames_OsOOOOO_7(memview_subi,fmt,memview_dims,memview_sp,memview_namedaxisidxs,memview___tmp_198,memview___tmp_199)
      if _res_generateconnames != 0:
        _,_msg_generateconnames = self.__getlasterror(_res_generateconnames)
        raise Error(rescode(_res_generateconnames),_msg_generateconnames)
    def generateconnames(self,*args,**kwds):
      """
      Generates systematic names for constraints.
    
      generateconnames(subi,fmt,dims,sp,namedaxisidxs,names)
        [dims : array(int32)]  Dimensions in the shape.  
        [fmt : str]  The constraint name formatting string.  
        [namedaxisidxs : array(int32)]  List if named index axes  
        [names : array(string)]  All axis names.  
        [sp : array(int64)]  Items that should be named.  
        [subi : array(int32)]  Indexes of the constraints.  
      """
      return self.__generateconnames_OsOOOOO_7(*args,**kwds)
    def __generateconenames_OsOOOOO_7(self,subk,fmt,dims,sp,namedaxisidxs,names):
      if subk is None:
        raise TypeError("Argument subk may not be None")
      copyback_subk = False
      if subk is None:
        subk_ = None
        memview_subk = None
      else:
        try:
          memview_subk = memoryview(subk)
        except TypeError:
          try:
            _tmparray_subk = array.array("i",subk)
          except TypeError:
            raise TypeError("Argument subk has wrong type") from None
          else:
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
        else:
          if memview_subk.ndim != 1:
            raise TypeError("Argument subk must be one-dimensional")
          if memview_subk.format != "i":
            _tmparray_subk = array.array("i",subk)
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
      if dims is None:
        raise TypeError("Argument dims may not be None")
      copyback_dims = False
      if dims is None:
        dims_ = None
        memview_dims = None
      else:
        try:
          memview_dims = memoryview(dims)
        except TypeError:
          try:
            _tmparray_dims = array.array("i",dims)
          except TypeError:
            raise TypeError("Argument dims has wrong type") from None
          else:
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
        else:
          if memview_dims.ndim != 1:
            raise TypeError("Argument dims must be one-dimensional")
          if memview_dims.format != "i":
            _tmparray_dims = array.array("i",dims)
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
      copyback_sp = False
      if sp is None:
        sp_ = None
        memview_sp = None
      else:
        try:
          memview_sp = memoryview(sp)
        except TypeError:
          try:
            _tmparray_sp = array.array("q",sp)
          except TypeError:
            raise TypeError("Argument sp has wrong type") from None
          else:
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
        else:
          if memview_sp.ndim != 1:
            raise TypeError("Argument sp must be one-dimensional")
          if memview_sp.format != "q":
            _tmparray_sp = array.array("q",sp)
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
      copyback_namedaxisidxs = False
      if namedaxisidxs is None:
        namedaxisidxs_ = None
        memview_namedaxisidxs = None
      else:
        try:
          memview_namedaxisidxs = memoryview(namedaxisidxs)
        except TypeError:
          try:
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
          except TypeError:
            raise TypeError("Argument namedaxisidxs has wrong type") from None
          else:
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
        else:
          if memview_namedaxisidxs.ndim != 1:
            raise TypeError("Argument namedaxisidxs must be one-dimensional")
          if memview_namedaxisidxs.format != "i":
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
      if names is not None:
        __tmp_218 = array.array("q")
        __tmp_219 = bytearray()
        for __tmp_220 in names:
          __tmp_218.append(len(__tmp_219))
          __tmp_219.extend(__tmp_220.encode("utf-8"))
          __tmp_219.append(0)
        __tmp_218.append(len(__tmp_219))
        __tmp_218.pop()
        memview___tmp_218   = memoryview(__tmp_218)
        memview___tmp_219 = memoryview(__tmp_219)
      else:
        memview___tmp_218   = None
        memview___tmp_219 = None
      _res_generateconenames,_retargs_generateconenames = self.__obj.generateconenames_OsOOOOO_7(memview_subk,fmt,memview_dims,memview_sp,memview_namedaxisidxs,memview___tmp_218,memview___tmp_219)
      if _res_generateconenames != 0:
        _,_msg_generateconenames = self.__getlasterror(_res_generateconenames)
        raise Error(rescode(_res_generateconenames),_msg_generateconenames)
    def generateconenames(self,*args,**kwds):
      """
      Generates systematic names for cone.
    
      generateconenames(subk,fmt,dims,sp,namedaxisidxs,names)
        [dims : array(int32)]  Dimensions in the shape.  
        [fmt : str]  The cone name formatting string.  
        [namedaxisidxs : array(int32)]  List if named index axes  
        [names : array(string)]  All axis names.  
        [sp : array(int64)]  Items that should be named.  
        [subk : array(int32)]  Indexes of the cone.  
      """
      return self.__generateconenames_OsOOOOO_7(*args,**kwds)
    def __generateaccnames_OsOOOOO_7(self,sub,fmt,dims,sp,namedaxisidxs,names):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("q",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "q":
            _tmparray_sub = array.array("q",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if dims is None:
        raise TypeError("Argument dims may not be None")
      copyback_dims = False
      if dims is None:
        dims_ = None
        memview_dims = None
      else:
        try:
          memview_dims = memoryview(dims)
        except TypeError:
          try:
            _tmparray_dims = array.array("i",dims)
          except TypeError:
            raise TypeError("Argument dims has wrong type") from None
          else:
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
        else:
          if memview_dims.ndim != 1:
            raise TypeError("Argument dims must be one-dimensional")
          if memview_dims.format != "i":
            _tmparray_dims = array.array("i",dims)
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
      copyback_sp = False
      if sp is None:
        sp_ = None
        memview_sp = None
      else:
        try:
          memview_sp = memoryview(sp)
        except TypeError:
          try:
            _tmparray_sp = array.array("q",sp)
          except TypeError:
            raise TypeError("Argument sp has wrong type") from None
          else:
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
        else:
          if memview_sp.ndim != 1:
            raise TypeError("Argument sp must be one-dimensional")
          if memview_sp.format != "q":
            _tmparray_sp = array.array("q",sp)
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
      copyback_namedaxisidxs = False
      if namedaxisidxs is None:
        namedaxisidxs_ = None
        memview_namedaxisidxs = None
      else:
        try:
          memview_namedaxisidxs = memoryview(namedaxisidxs)
        except TypeError:
          try:
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
          except TypeError:
            raise TypeError("Argument namedaxisidxs has wrong type") from None
          else:
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
        else:
          if memview_namedaxisidxs.ndim != 1:
            raise TypeError("Argument namedaxisidxs must be one-dimensional")
          if memview_namedaxisidxs.format != "i":
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
      if names is not None:
        __tmp_238 = array.array("q")
        __tmp_239 = bytearray()
        for __tmp_240 in names:
          __tmp_238.append(len(__tmp_239))
          __tmp_239.extend(__tmp_240.encode("utf-8"))
          __tmp_239.append(0)
        __tmp_238.append(len(__tmp_239))
        __tmp_238.pop()
        memview___tmp_238   = memoryview(__tmp_238)
        memview___tmp_239 = memoryview(__tmp_239)
      else:
        memview___tmp_238   = None
        memview___tmp_239 = None
      _res_generateaccnames,_retargs_generateaccnames = self.__obj.generateaccnames_OsOOOOO_7(memview_sub,fmt,memview_dims,memview_sp,memview_namedaxisidxs,memview___tmp_238,memview___tmp_239)
      if _res_generateaccnames != 0:
        _,_msg_generateaccnames = self.__getlasterror(_res_generateaccnames)
        raise Error(rescode(_res_generateaccnames),_msg_generateaccnames)
    def generateaccnames(self,*args,**kwds):
      """
      Generates systematic names for affine conic constraints.
    
      generateaccnames(sub,fmt,dims,sp,namedaxisidxs,names)
        [dims : array(int32)]  Dimensions in the shape.  
        [fmt : str]  The variable name formatting string.  
        [namedaxisidxs : array(int32)]  List if named index axes  
        [names : array(string)]  All axis names.  
        [sp : array(int64)]  Items that should be named.  
        [sub : array(int64)]  Indexes of the affine conic constraints.  
      """
      return self.__generateaccnames_OsOOOOO_7(*args,**kwds)
    def __generatedjcnames_OsOOOOO_7(self,sub,fmt,dims,sp,namedaxisidxs,names):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("q",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "q":
            _tmparray_sub = array.array("q",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if dims is None:
        raise TypeError("Argument dims may not be None")
      copyback_dims = False
      if dims is None:
        dims_ = None
        memview_dims = None
      else:
        try:
          memview_dims = memoryview(dims)
        except TypeError:
          try:
            _tmparray_dims = array.array("i",dims)
          except TypeError:
            raise TypeError("Argument dims has wrong type") from None
          else:
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
        else:
          if memview_dims.ndim != 1:
            raise TypeError("Argument dims must be one-dimensional")
          if memview_dims.format != "i":
            _tmparray_dims = array.array("i",dims)
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
      copyback_sp = False
      if sp is None:
        sp_ = None
        memview_sp = None
      else:
        try:
          memview_sp = memoryview(sp)
        except TypeError:
          try:
            _tmparray_sp = array.array("q",sp)
          except TypeError:
            raise TypeError("Argument sp has wrong type") from None
          else:
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
        else:
          if memview_sp.ndim != 1:
            raise TypeError("Argument sp must be one-dimensional")
          if memview_sp.format != "q":
            _tmparray_sp = array.array("q",sp)
            memview_sp = memoryview(_tmparray_sp)
            copyback_sp = True
            sp_ = _tmparray_sp
      copyback_namedaxisidxs = False
      if namedaxisidxs is None:
        namedaxisidxs_ = None
        memview_namedaxisidxs = None
      else:
        try:
          memview_namedaxisidxs = memoryview(namedaxisidxs)
        except TypeError:
          try:
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
          except TypeError:
            raise TypeError("Argument namedaxisidxs has wrong type") from None
          else:
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
        else:
          if memview_namedaxisidxs.ndim != 1:
            raise TypeError("Argument namedaxisidxs must be one-dimensional")
          if memview_namedaxisidxs.format != "i":
            _tmparray_namedaxisidxs = array.array("i",namedaxisidxs)
            memview_namedaxisidxs = memoryview(_tmparray_namedaxisidxs)
            copyback_namedaxisidxs = True
            namedaxisidxs_ = _tmparray_namedaxisidxs
      if names is not None:
        __tmp_258 = array.array("q")
        __tmp_259 = bytearray()
        for __tmp_260 in names:
          __tmp_258.append(len(__tmp_259))
          __tmp_259.extend(__tmp_260.encode("utf-8"))
          __tmp_259.append(0)
        __tmp_258.append(len(__tmp_259))
        __tmp_258.pop()
        memview___tmp_258   = memoryview(__tmp_258)
        memview___tmp_259 = memoryview(__tmp_259)
      else:
        memview___tmp_258   = None
        memview___tmp_259 = None
      _res_generatedjcnames,_retargs_generatedjcnames = self.__obj.generatedjcnames_OsOOOOO_7(memview_sub,fmt,memview_dims,memview_sp,memview_namedaxisidxs,memview___tmp_258,memview___tmp_259)
      if _res_generatedjcnames != 0:
        _,_msg_generatedjcnames = self.__getlasterror(_res_generatedjcnames)
        raise Error(rescode(_res_generatedjcnames),_msg_generatedjcnames)
    def generatedjcnames(self,*args,**kwds):
      """
      Generates systematic names for affine conic constraints.
    
      generatedjcnames(sub,fmt,dims,sp,namedaxisidxs,names)
        [dims : array(int32)]  Dimensions in the shape.  
        [fmt : str]  The variable name formatting string.  
        [namedaxisidxs : array(int32)]  List if named index axes  
        [names : array(string)]  All axis names.  
        [sp : array(int64)]  Items that should be named.  
        [sub : array(int64)]  Indexes of the disjunctive constraints.  
      """
      return self.__generatedjcnames_OsOOOOO_7(*args,**kwds)
    def __putconname_is_3(self,i,name):
      _res_putconname,_retargs_putconname = self.__obj.putconname_is_3(i,name)
      if _res_putconname != 0:
        _,_msg_putconname = self.__getlasterror(_res_putconname)
        raise Error(rescode(_res_putconname),_msg_putconname)
    def putconname(self,*args,**kwds):
      """
      Sets the name of a constraint.
    
      putconname(i,name)
        [i : int32]  Index of the constraint.  
        [name : str]  The name of the constraint.  
      """
      return self.__putconname_is_3(*args,**kwds)
    def __putvarname_is_3(self,j,name):
      _res_putvarname,_retargs_putvarname = self.__obj.putvarname_is_3(j,name)
      if _res_putvarname != 0:
        _,_msg_putvarname = self.__getlasterror(_res_putvarname)
        raise Error(rescode(_res_putvarname),_msg_putvarname)
    def putvarname(self,*args,**kwds):
      """
      Sets the name of a variable.
    
      putvarname(j,name)
        [j : int32]  Index of the variable.  
        [name : str]  The variable name.  
      """
      return self.__putvarname_is_3(*args,**kwds)
    def __putconename_is_3(self,j,name):
      _res_putconename,_retargs_putconename = self.__obj.putconename_is_3(j,name)
      if _res_putconename != 0:
        _,_msg_putconename = self.__getlasterror(_res_putconename)
        raise Error(rescode(_res_putconename),_msg_putconename)
    def putconename(self,*args,**kwds):
      """
      Sets the name of a cone.
    
      putconename(j,name)
        [j : int32]  Index of the cone.  
        [name : str]  The name of the cone.  
      """
      return self.__putconename_is_3(*args,**kwds)
    def __putbarvarname_is_3(self,j,name):
      _res_putbarvarname,_retargs_putbarvarname = self.__obj.putbarvarname_is_3(j,name)
      if _res_putbarvarname != 0:
        _,_msg_putbarvarname = self.__getlasterror(_res_putbarvarname)
        raise Error(rescode(_res_putbarvarname),_msg_putbarvarname)
    def putbarvarname(self,*args,**kwds):
      """
      Sets the name of a semidefinite variable.
    
      putbarvarname(j,name)
        [j : int32]  Index of the variable.  
        [name : str]  The variable name.  
      """
      return self.__putbarvarname_is_3(*args,**kwds)
    def __putdomainname_Ls_3(self,domidx,name):
      _res_putdomainname,_retargs_putdomainname = self.__obj.putdomainname_Ls_3(domidx,name)
      if _res_putdomainname != 0:
        _,_msg_putdomainname = self.__getlasterror(_res_putdomainname)
        raise Error(rescode(_res_putdomainname),_msg_putdomainname)
    def putdomainname(self,*args,**kwds):
      """
      Sets the name of a domain.
    
      putdomainname(domidx,name)
        [domidx : int64]  Index of the domain.  
        [name : str]  The name of the domain.  
      """
      return self.__putdomainname_Ls_3(*args,**kwds)
    def __putdjcname_Ls_3(self,djcidx,name):
      _res_putdjcname,_retargs_putdjcname = self.__obj.putdjcname_Ls_3(djcidx,name)
      if _res_putdjcname != 0:
        _,_msg_putdjcname = self.__getlasterror(_res_putdjcname)
        raise Error(rescode(_res_putdjcname),_msg_putdjcname)
    def putdjcname(self,*args,**kwds):
      """
      Sets the name of a disjunctive constraint.
    
      putdjcname(djcidx,name)
        [djcidx : int64]  Index of the disjunctive constraint.  
        [name : str]  The name of the disjunctive constraint.  
      """
      return self.__putdjcname_Ls_3(*args,**kwds)
    def __putaccname_Ls_3(self,accidx,name):
      _res_putaccname,_retargs_putaccname = self.__obj.putaccname_Ls_3(accidx,name)
      if _res_putaccname != 0:
        _,_msg_putaccname = self.__getlasterror(_res_putaccname)
        raise Error(rescode(_res_putaccname),_msg_putaccname)
    def putaccname(self,*args,**kwds):
      """
      Sets the name of an affine conic constraint.
    
      putaccname(accidx,name)
        [accidx : int64]  Index of the affine conic constraint.  
        [name : str]  The name of the affine conic constraint.  
      """
      return self.__putaccname_Ls_3(*args,**kwds)
    def __getvarnamelen_i_2(self,i):
      _res_getvarnamelen,_retargs_getvarnamelen = self.__obj.getvarnamelen_i_2(i)
      if _res_getvarnamelen != 0:
        _,_msg_getvarnamelen = self.__getlasterror(_res_getvarnamelen)
        raise Error(rescode(_res_getvarnamelen),_msg_getvarnamelen)
      else:
        (len) = _retargs_getvarnamelen
      return (len)
    def getvarnamelen(self,*args,**kwds):
      """
      Obtains the length of the name of a variable.
    
      getvarnamelen(i) -> (len)
        [i : int32]  Index of a variable.  
        [len : int32]  Returns the length of the indicated name.  
      """
      return self.__getvarnamelen_i_2(*args,**kwds)
    def __getvarname_iO_2(self,j):
      name = bytearray(0)
      _res_getvarname,_retargs_getvarname = self.__obj.getvarname_iO_2(j,name)
      if _res_getvarname != 0:
        _,_msg_getvarname = self.__getlasterror(_res_getvarname)
        raise Error(rescode(_res_getvarname),_msg_getvarname)
      __tmp_276 = name.find(b"\0")
      if __tmp_276 >= 0:
        name = name[:__tmp_276]
      return (name.decode("utf-8",errors="ignore"))
    def getvarname(self,*args,**kwds):
      """
      Obtains the name of a variable.
    
      getvarname(j) -> (name)
        [j : int32]  Index of a variable.  
        [name : str]  Returns the required name.  
      """
      return self.__getvarname_iO_2(*args,**kwds)
    def __getconnamelen_i_2(self,i):
      _res_getconnamelen,_retargs_getconnamelen = self.__obj.getconnamelen_i_2(i)
      if _res_getconnamelen != 0:
        _,_msg_getconnamelen = self.__getlasterror(_res_getconnamelen)
        raise Error(rescode(_res_getconnamelen),_msg_getconnamelen)
      else:
        (len) = _retargs_getconnamelen
      return (len)
    def getconnamelen(self,*args,**kwds):
      """
      Obtains the length of the name of a constraint.
    
      getconnamelen(i) -> (len)
        [i : int32]  Index of the constraint.  
        [len : int32]  Returns the length of the indicated name.  
      """
      return self.__getconnamelen_i_2(*args,**kwds)
    def __getconname_iO_2(self,i):
      name = bytearray(0)
      _res_getconname,_retargs_getconname = self.__obj.getconname_iO_2(i,name)
      if _res_getconname != 0:
        _,_msg_getconname = self.__getlasterror(_res_getconname)
        raise Error(rescode(_res_getconname),_msg_getconname)
      __tmp_282 = name.find(b"\0")
      if __tmp_282 >= 0:
        name = name[:__tmp_282]
      return (name.decode("utf-8",errors="ignore"))
    def getconname(self,*args,**kwds):
      """
      Obtains the name of a constraint.
    
      getconname(i) -> (name)
        [i : int32]  Index of the constraint.  
        [name : str]  The required name.  
      """
      return self.__getconname_iO_2(*args,**kwds)
    def __getconnameindex_s_2(self,somename):
      _res_getconnameindex,_retargs_getconnameindex = self.__obj.getconnameindex_s_2(somename)
      if _res_getconnameindex != 0:
        _,_msg_getconnameindex = self.__getlasterror(_res_getconnameindex)
        raise Error(rescode(_res_getconnameindex),_msg_getconnameindex)
      else:
        (asgn,index) = _retargs_getconnameindex
      return (asgn,index)
    def getconnameindex(self,*args,**kwds):
      """
      Checks whether the name has been assigned to any constraint.
    
      getconnameindex(somename) -> (asgn,index)
        [asgn : int32]  Is non-zero if the name somename is assigned to some constraint.  
        [index : int32]  If the name somename is assigned to a constraint, then return the index of the constraint.  
        [somename : str]  The name which should be checked.  
      """
      return self.__getconnameindex_s_2(*args,**kwds)
    def __getvarnameindex_s_2(self,somename):
      _res_getvarnameindex,_retargs_getvarnameindex = self.__obj.getvarnameindex_s_2(somename)
      if _res_getvarnameindex != 0:
        _,_msg_getvarnameindex = self.__getlasterror(_res_getvarnameindex)
        raise Error(rescode(_res_getvarnameindex),_msg_getvarnameindex)
      else:
        (asgn,index) = _retargs_getvarnameindex
      return (asgn,index)
    def getvarnameindex(self,*args,**kwds):
      """
      Checks whether the name has been assigned to any variable.
    
      getvarnameindex(somename) -> (asgn,index)
        [asgn : int32]  Is non-zero if the name somename is assigned to a variable.  
        [index : int32]  If the name somename is assigned to a variable, then return the index of the variable.  
        [somename : str]  The name which should be checked.  
      """
      return self.__getvarnameindex_s_2(*args,**kwds)
    def __getconenamelen_i_2(self,i):
      _res_getconenamelen,_retargs_getconenamelen = self.__obj.getconenamelen_i_2(i)
      if _res_getconenamelen != 0:
        _,_msg_getconenamelen = self.__getlasterror(_res_getconenamelen)
        raise Error(rescode(_res_getconenamelen),_msg_getconenamelen)
      else:
        (len) = _retargs_getconenamelen
      return (len)
    def getconenamelen(self,*args,**kwds):
      """
      Obtains the length of the name of a cone.
    
      getconenamelen(i) -> (len)
        [i : int32]  Index of the cone.  
        [len : int32]  Returns the length of the indicated name.  
      """
      return self.__getconenamelen_i_2(*args,**kwds)
    def __getconename_iO_2(self,i):
      name = bytearray(0)
      _res_getconename,_retargs_getconename = self.__obj.getconename_iO_2(i,name)
      if _res_getconename != 0:
        _,_msg_getconename = self.__getlasterror(_res_getconename)
        raise Error(rescode(_res_getconename),_msg_getconename)
      __tmp_288 = name.find(b"\0")
      if __tmp_288 >= 0:
        name = name[:__tmp_288]
      return (name.decode("utf-8",errors="ignore"))
    def getconename(self,*args,**kwds):
      """
      Obtains the name of a cone.
    
      getconename(i) -> (name)
        [i : int32]  Index of the cone.  
        [name : str]  The required name.  
      """
      return self.__getconename_iO_2(*args,**kwds)
    def __getconenameindex_s_2(self,somename):
      _res_getconenameindex,_retargs_getconenameindex = self.__obj.getconenameindex_s_2(somename)
      if _res_getconenameindex != 0:
        _,_msg_getconenameindex = self.__getlasterror(_res_getconenameindex)
        raise Error(rescode(_res_getconenameindex),_msg_getconenameindex)
      else:
        (asgn,index) = _retargs_getconenameindex
      return (asgn,index)
    def getconenameindex(self,*args,**kwds):
      """
      Checks whether the name has been assigned to any cone.
    
      getconenameindex(somename) -> (asgn,index)
        [asgn : int32]  Is non-zero if the name somename is assigned to some cone.  
        [index : int32]  If the name somename is assigned to some cone, this is the index of the cone.  
        [somename : str]  The name which should be checked.  
      """
      return self.__getconenameindex_s_2(*args,**kwds)
    def __getdomainnamelen_L_2(self,domidx):
      _res_getdomainnamelen,_retargs_getdomainnamelen = self.__obj.getdomainnamelen_L_2(domidx)
      if _res_getdomainnamelen != 0:
        _,_msg_getdomainnamelen = self.__getlasterror(_res_getdomainnamelen)
        raise Error(rescode(_res_getdomainnamelen),_msg_getdomainnamelen)
      else:
        (len) = _retargs_getdomainnamelen
      return (len)
    def getdomainnamelen(self,*args,**kwds):
      """
      Obtains the length of the name of a domain.
    
      getdomainnamelen(domidx) -> (len)
        [domidx : int64]  Index of a domain.  
        [len : int32]  Returns the length of the indicated name.  
      """
      return self.__getdomainnamelen_L_2(*args,**kwds)
    def __getdomainname_LO_2(self,domidx):
      name = bytearray(0)
      _res_getdomainname,_retargs_getdomainname = self.__obj.getdomainname_LO_2(domidx,name)
      if _res_getdomainname != 0:
        _,_msg_getdomainname = self.__getlasterror(_res_getdomainname)
        raise Error(rescode(_res_getdomainname),_msg_getdomainname)
      __tmp_294 = name.find(b"\0")
      if __tmp_294 >= 0:
        name = name[:__tmp_294]
      return (name.decode("utf-8",errors="ignore"))
    def getdomainname(self,*args,**kwds):
      """
      Obtains the name of a domain.
    
      getdomainname(domidx) -> (name)
        [domidx : int64]  Index of a domain.  
        [name : str]  Returns the required name.  
      """
      return self.__getdomainname_LO_2(*args,**kwds)
    def __getdjcnamelen_L_2(self,djcidx):
      _res_getdjcnamelen,_retargs_getdjcnamelen = self.__obj.getdjcnamelen_L_2(djcidx)
      if _res_getdjcnamelen != 0:
        _,_msg_getdjcnamelen = self.__getlasterror(_res_getdjcnamelen)
        raise Error(rescode(_res_getdjcnamelen),_msg_getdjcnamelen)
      else:
        (len) = _retargs_getdjcnamelen
      return (len)
    def getdjcnamelen(self,*args,**kwds):
      """
      Obtains the length of the name of a disjunctive constraint.
    
      getdjcnamelen(djcidx) -> (len)
        [djcidx : int64]  Index of a disjunctive constraint.  
        [len : int32]  Returns the length of the indicated name.  
      """
      return self.__getdjcnamelen_L_2(*args,**kwds)
    def __getdjcname_LO_2(self,djcidx):
      name = bytearray(0)
      _res_getdjcname,_retargs_getdjcname = self.__obj.getdjcname_LO_2(djcidx,name)
      if _res_getdjcname != 0:
        _,_msg_getdjcname = self.__getlasterror(_res_getdjcname)
        raise Error(rescode(_res_getdjcname),_msg_getdjcname)
      __tmp_300 = name.find(b"\0")
      if __tmp_300 >= 0:
        name = name[:__tmp_300]
      return (name.decode("utf-8",errors="ignore"))
    def getdjcname(self,*args,**kwds):
      """
      Obtains the name of a disjunctive constraint.
    
      getdjcname(djcidx) -> (name)
        [djcidx : int64]  Index of a disjunctive constraint.  
        [name : str]  Returns the required name.  
      """
      return self.__getdjcname_LO_2(*args,**kwds)
    def __getaccnamelen_L_2(self,accidx):
      _res_getaccnamelen,_retargs_getaccnamelen = self.__obj.getaccnamelen_L_2(accidx)
      if _res_getaccnamelen != 0:
        _,_msg_getaccnamelen = self.__getlasterror(_res_getaccnamelen)
        raise Error(rescode(_res_getaccnamelen),_msg_getaccnamelen)
      else:
        (len) = _retargs_getaccnamelen
      return (len)
    def getaccnamelen(self,*args,**kwds):
      """
      Obtains the length of the name of an affine conic constraint.
    
      getaccnamelen(accidx) -> (len)
        [accidx : int64]  Index of an affine conic constraint.  
        [len : int32]  Returns the length of the indicated name.  
      """
      return self.__getaccnamelen_L_2(*args,**kwds)
    def __getaccname_LO_2(self,accidx):
      name = bytearray(0)
      _res_getaccname,_retargs_getaccname = self.__obj.getaccname_LO_2(accidx,name)
      if _res_getaccname != 0:
        _,_msg_getaccname = self.__getlasterror(_res_getaccname)
        raise Error(rescode(_res_getaccname),_msg_getaccname)
      __tmp_306 = name.find(b"\0")
      if __tmp_306 >= 0:
        name = name[:__tmp_306]
      return (name.decode("utf-8",errors="ignore"))
    def getaccname(self,*args,**kwds):
      """
      Obtains the name of an affine conic constraint.
    
      getaccname(accidx) -> (name)
        [accidx : int64]  Index of an affine conic constraint.  
        [name : str]  Returns the required name.  
      """
      return self.__getaccname_LO_2(*args,**kwds)
    def __getnumanz__1(self):
      _res_getnumanz,_retargs_getnumanz = self.__obj.getnumanz__1()
      if _res_getnumanz != 0:
        _,_msg_getnumanz = self.__getlasterror(_res_getnumanz)
        raise Error(rescode(_res_getnumanz),_msg_getnumanz)
      else:
        (numanz) = _retargs_getnumanz
      return (numanz)
    def getnumanz(self,*args,**kwds):
      """
      Obtains the number of non-zeros in the coefficient matrix.
    
      getnumanz() -> (numanz)
        [numanz : int32]  Number of non-zero elements in the linear constraint matrix.  
      """
      return self.__getnumanz__1(*args,**kwds)
    def __getnumanz64__1(self):
      _res_getnumanz64,_retargs_getnumanz64 = self.__obj.getnumanz64__1()
      if _res_getnumanz64 != 0:
        _,_msg_getnumanz64 = self.__getlasterror(_res_getnumanz64)
        raise Error(rescode(_res_getnumanz64),_msg_getnumanz64)
      else:
        (numanz) = _retargs_getnumanz64
      return (numanz)
    def getnumanz64(self,*args,**kwds):
      """
      Obtains the number of non-zeros in the coefficient matrix.
    
      getnumanz64() -> (numanz)
        [numanz : int64]  Number of non-zero elements in the linear constraint matrix.  
      """
      return self.__getnumanz64__1(*args,**kwds)
    def __getnumcon__1(self):
      _res_getnumcon,_retargs_getnumcon = self.__obj.getnumcon__1()
      if _res_getnumcon != 0:
        _,_msg_getnumcon = self.__getlasterror(_res_getnumcon)
        raise Error(rescode(_res_getnumcon),_msg_getnumcon)
      else:
        (numcon) = _retargs_getnumcon
      return (numcon)
    def getnumcon(self,*args,**kwds):
      """
      Obtains the number of constraints.
    
      getnumcon() -> (numcon)
        [numcon : int32]  Number of constraints.  
      """
      return self.__getnumcon__1(*args,**kwds)
    def __getnumcone__1(self):
      _res_getnumcone,_retargs_getnumcone = self.__obj.getnumcone__1()
      if _res_getnumcone != 0:
        _,_msg_getnumcone = self.__getlasterror(_res_getnumcone)
        raise Error(rescode(_res_getnumcone),_msg_getnumcone)
      else:
        (numcone) = _retargs_getnumcone
      return (numcone)
    def getnumcone(self,*args,**kwds):
      """
      Obtains the number of cones.
    
      getnumcone() -> (numcone)
        [numcone : int32]  Number of conic constraints.  
      """
      return self.__getnumcone__1(*args,**kwds)
    def __getnumconemem_i_2(self,k):
      _res_getnumconemem,_retargs_getnumconemem = self.__obj.getnumconemem_i_2(k)
      if _res_getnumconemem != 0:
        _,_msg_getnumconemem = self.__getlasterror(_res_getnumconemem)
        raise Error(rescode(_res_getnumconemem),_msg_getnumconemem)
      else:
        (nummem) = _retargs_getnumconemem
      return (nummem)
    def getnumconemem(self,*args,**kwds):
      """
      Obtains the number of members in a cone.
    
      getnumconemem(k) -> (nummem)
        [k : int32]  Index of the cone.  
        [nummem : int32]  Number of member variables in the cone.  
      """
      return self.__getnumconemem_i_2(*args,**kwds)
    def __getnumintvar__1(self):
      _res_getnumintvar,_retargs_getnumintvar = self.__obj.getnumintvar__1()
      if _res_getnumintvar != 0:
        _,_msg_getnumintvar = self.__getlasterror(_res_getnumintvar)
        raise Error(rescode(_res_getnumintvar),_msg_getnumintvar)
      else:
        (numintvar) = _retargs_getnumintvar
      return (numintvar)
    def getnumintvar(self,*args,**kwds):
      """
      Obtains the number of integer-constrained variables.
    
      getnumintvar() -> (numintvar)
        [numintvar : int32]  Number of integer variables.  
      """
      return self.__getnumintvar__1(*args,**kwds)
    def __getnumparam_i_2(self,partype):
      _res_getnumparam,_retargs_getnumparam = self.__obj.getnumparam_i_2(partype)
      if _res_getnumparam != 0:
        _,_msg_getnumparam = self.__getlasterror(_res_getnumparam)
        raise Error(rescode(_res_getnumparam),_msg_getnumparam)
      else:
        (numparam) = _retargs_getnumparam
      return (numparam)
    def getnumparam(self,*args,**kwds):
      """
      Obtains the number of parameters of a given type.
    
      getnumparam(partype) -> (numparam)
        [numparam : int32]  Returns the number of parameters of the requested type.  
        [partype : mosek.parametertype]  Parameter type.  
      """
      return self.__getnumparam_i_2(*args,**kwds)
    def __getnumqconknz64_i_2(self,k):
      _res_getnumqconknz64,_retargs_getnumqconknz64 = self.__obj.getnumqconknz64_i_2(k)
      if _res_getnumqconknz64 != 0:
        _,_msg_getnumqconknz64 = self.__getlasterror(_res_getnumqconknz64)
        raise Error(rescode(_res_getnumqconknz64),_msg_getnumqconknz64)
      else:
        (numqcnz) = _retargs_getnumqconknz64
      return (numqcnz)
    def getnumqconknz(self,*args,**kwds):
      """
      Obtains the number of non-zero quadratic terms in a constraint.
    
      getnumqconknz(k) -> (numqcnz)
        [k : int32]  Index of the constraint for which the number quadratic terms should be obtained.  
        [numqcnz : int64]  Number of quadratic terms.  
      """
      return self.__getnumqconknz64_i_2(*args,**kwds)
    def __getnumqobjnz64__1(self):
      _res_getnumqobjnz64,_retargs_getnumqobjnz64 = self.__obj.getnumqobjnz64__1()
      if _res_getnumqobjnz64 != 0:
        _,_msg_getnumqobjnz64 = self.__getlasterror(_res_getnumqobjnz64)
        raise Error(rescode(_res_getnumqobjnz64),_msg_getnumqobjnz64)
      else:
        (numqonz) = _retargs_getnumqobjnz64
      return (numqonz)
    def getnumqobjnz(self,*args,**kwds):
      """
      Obtains the number of non-zero quadratic terms in the objective.
    
      getnumqobjnz() -> (numqonz)
        [numqonz : int64]  Number of non-zero elements in the quadratic objective terms.  
      """
      return self.__getnumqobjnz64__1(*args,**kwds)
    def __getnumvar__1(self):
      _res_getnumvar,_retargs_getnumvar = self.__obj.getnumvar__1()
      if _res_getnumvar != 0:
        _,_msg_getnumvar = self.__getlasterror(_res_getnumvar)
        raise Error(rescode(_res_getnumvar),_msg_getnumvar)
      else:
        (numvar) = _retargs_getnumvar
      return (numvar)
    def getnumvar(self,*args,**kwds):
      """
      Obtains the number of variables.
    
      getnumvar() -> (numvar)
        [numvar : int32]  Number of variables.  
      """
      return self.__getnumvar__1(*args,**kwds)
    def __getnumbarvar__1(self):
      _res_getnumbarvar,_retargs_getnumbarvar = self.__obj.getnumbarvar__1()
      if _res_getnumbarvar != 0:
        _,_msg_getnumbarvar = self.__getlasterror(_res_getnumbarvar)
        raise Error(rescode(_res_getnumbarvar),_msg_getnumbarvar)
      else:
        (numbarvar) = _retargs_getnumbarvar
      return (numbarvar)
    def getnumbarvar(self,*args,**kwds):
      """
      Obtains the number of semidefinite variables.
    
      getnumbarvar() -> (numbarvar)
        [numbarvar : int32]  Number of semidefinite variables in the problem.  
      """
      return self.__getnumbarvar__1(*args,**kwds)
    def __getmaxnumbarvar__1(self):
      _res_getmaxnumbarvar,_retargs_getmaxnumbarvar = self.__obj.getmaxnumbarvar__1()
      if _res_getmaxnumbarvar != 0:
        _,_msg_getmaxnumbarvar = self.__getlasterror(_res_getmaxnumbarvar)
        raise Error(rescode(_res_getmaxnumbarvar),_msg_getmaxnumbarvar)
      else:
        (maxnumbarvar) = _retargs_getmaxnumbarvar
      return (maxnumbarvar)
    def getmaxnumbarvar(self,*args,**kwds):
      """
      Obtains maximum number of symmetric matrix variables for which space is currently preallocated.
    
      getmaxnumbarvar() -> (maxnumbarvar)
        [maxnumbarvar : int32]  Maximum number of symmetric matrix variables for which space is currently preallocated.  
      """
      return self.__getmaxnumbarvar__1(*args,**kwds)
    def __getdimbarvarj_i_2(self,j):
      _res_getdimbarvarj,_retargs_getdimbarvarj = self.__obj.getdimbarvarj_i_2(j)
      if _res_getdimbarvarj != 0:
        _,_msg_getdimbarvarj = self.__getlasterror(_res_getdimbarvarj)
        raise Error(rescode(_res_getdimbarvarj),_msg_getdimbarvarj)
      else:
        (dimbarvarj) = _retargs_getdimbarvarj
      return (dimbarvarj)
    def getdimbarvarj(self,*args,**kwds):
      """
      Obtains the dimension of a symmetric matrix variable.
    
      getdimbarvarj(j) -> (dimbarvarj)
        [dimbarvarj : int32]  The dimension of the j'th semidefinite variable.  
        [j : int32]  Index of the semidefinite variable whose dimension is requested.  
      """
      return self.__getdimbarvarj_i_2(*args,**kwds)
    def __getlenbarvarj_i_2(self,j):
      _res_getlenbarvarj,_retargs_getlenbarvarj = self.__obj.getlenbarvarj_i_2(j)
      if _res_getlenbarvarj != 0:
        _,_msg_getlenbarvarj = self.__getlasterror(_res_getlenbarvarj)
        raise Error(rescode(_res_getlenbarvarj),_msg_getlenbarvarj)
      else:
        (lenbarvarj) = _retargs_getlenbarvarj
      return (lenbarvarj)
    def getlenbarvarj(self,*args,**kwds):
      """
      Obtains the length of one semidefinite variable.
    
      getlenbarvarj(j) -> (lenbarvarj)
        [j : int32]  Index of the semidefinite variable whose length if requested.  
        [lenbarvarj : int64]  Number of scalar elements in the lower triangular part of the semidefinite variable.  
      """
      return self.__getlenbarvarj_i_2(*args,**kwds)
    def __getobjname_O_1(self):
      objname = bytearray(0)
      _res_getobjname,_retargs_getobjname = self.__obj.getobjname_O_1(objname)
      if _res_getobjname != 0:
        _,_msg_getobjname = self.__getlasterror(_res_getobjname)
        raise Error(rescode(_res_getobjname),_msg_getobjname)
      __tmp_312 = objname.find(b"\0")
      if __tmp_312 >= 0:
        objname = objname[:__tmp_312]
      return (objname.decode("utf-8",errors="ignore"))
    def getobjname(self,*args,**kwds):
      """
      Obtains the name assigned to the objective function.
    
      getobjname() -> (objname)
        [objname : str]  Assigned the objective name.  
      """
      return self.__getobjname_O_1(*args,**kwds)
    def __getobjnamelen__1(self):
      _res_getobjnamelen,_retargs_getobjnamelen = self.__obj.getobjnamelen__1()
      if _res_getobjnamelen != 0:
        _,_msg_getobjnamelen = self.__getlasterror(_res_getobjnamelen)
        raise Error(rescode(_res_getobjnamelen),_msg_getobjnamelen)
      else:
        (len) = _retargs_getobjnamelen
      return (len)
    def getobjnamelen(self,*args,**kwds):
      """
      Obtains the length of the name assigned to the objective function.
    
      getobjnamelen() -> (len)
        [len : int32]  Assigned the length of the objective name.  
      """
      return self.__getobjnamelen__1(*args,**kwds)
    def __getprimalobj_i_2(self,whichsol):
      _res_getprimalobj,_retargs_getprimalobj = self.__obj.getprimalobj_i_2(whichsol)
      if _res_getprimalobj != 0:
        _,_msg_getprimalobj = self.__getlasterror(_res_getprimalobj)
        raise Error(rescode(_res_getprimalobj),_msg_getprimalobj)
      else:
        (primalobj) = _retargs_getprimalobj
      return (primalobj)
    def getprimalobj(self,*args,**kwds):
      """
      Computes the primal objective value for the desired solution.
    
      getprimalobj(whichsol) -> (primalobj)
        [primalobj : float64]  Objective value corresponding to the primal solution.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__getprimalobj_i_2(*args,**kwds)
    def __getprobtype__1(self):
      _res_getprobtype,_retargs_getprobtype = self.__obj.getprobtype__1()
      if _res_getprobtype != 0:
        _,_msg_getprobtype = self.__getlasterror(_res_getprobtype)
        raise Error(rescode(_res_getprobtype),_msg_getprobtype)
      else:
        (probtype) = _retargs_getprobtype
      return (problemtype(probtype))
    def getprobtype(self,*args,**kwds):
      """
      Obtains the problem type.
    
      getprobtype() -> (probtype)
        [probtype : mosek.problemtype]  The problem type.  
      """
      return self.__getprobtype__1(*args,**kwds)
    def __getqconk64_iOOO_5(self,k,qcsubi,qcsubj,qcval):
      if qcsubi is None:
        raise TypeError("Argument qcsubi may not be None")
      copyback_qcsubi = False
      if qcsubi is None:
        qcsubi_ = None
        memview_qcsubi = None
      else:
        try:
          memview_qcsubi = memoryview(qcsubi)
        except TypeError:
          try:
            _tmparray_qcsubi = array.array("i",[0 for _ in range(len(qcsubi))])
          except TypeError:
            raise TypeError("Argument qcsubi has wrong type") from None
          else:
            memview_qcsubi = memoryview(_tmparray_qcsubi)
            copyback_qcsubi = True
            qcsubi_ = _tmparray_qcsubi
        else:
          if memview_qcsubi.ndim != 1:
            raise TypeError("Argument qcsubi must be one-dimensional")
          if memview_qcsubi.format != "i":
            _tmparray_qcsubi = array.array("i",qcsubi)
            memview_qcsubi = memoryview(_tmparray_qcsubi)
            copyback_qcsubi = True
            qcsubi_ = _tmparray_qcsubi
      if qcsubj is None:
        raise TypeError("Argument qcsubj may not be None")
      copyback_qcsubj = False
      if qcsubj is None:
        qcsubj_ = None
        memview_qcsubj = None
      else:
        try:
          memview_qcsubj = memoryview(qcsubj)
        except TypeError:
          try:
            _tmparray_qcsubj = array.array("i",[0 for _ in range(len(qcsubj))])
          except TypeError:
            raise TypeError("Argument qcsubj has wrong type") from None
          else:
            memview_qcsubj = memoryview(_tmparray_qcsubj)
            copyback_qcsubj = True
            qcsubj_ = _tmparray_qcsubj
        else:
          if memview_qcsubj.ndim != 1:
            raise TypeError("Argument qcsubj must be one-dimensional")
          if memview_qcsubj.format != "i":
            _tmparray_qcsubj = array.array("i",qcsubj)
            memview_qcsubj = memoryview(_tmparray_qcsubj)
            copyback_qcsubj = True
            qcsubj_ = _tmparray_qcsubj
      if qcval is None:
        raise TypeError("Argument qcval may not be None")
      copyback_qcval = False
      if qcval is None:
        qcval_ = None
        memview_qcval = None
      else:
        try:
          memview_qcval = memoryview(qcval)
        except TypeError:
          try:
            _tmparray_qcval = array.array("d",[0 for _ in range(len(qcval))])
          except TypeError:
            raise TypeError("Argument qcval has wrong type") from None
          else:
            memview_qcval = memoryview(_tmparray_qcval)
            copyback_qcval = True
            qcval_ = _tmparray_qcval
        else:
          if memview_qcval.ndim != 1:
            raise TypeError("Argument qcval must be one-dimensional")
          if memview_qcval.format != "d":
            _tmparray_qcval = array.array("d",qcval)
            memview_qcval = memoryview(_tmparray_qcval)
            copyback_qcval = True
            qcval_ = _tmparray_qcval
      _res_getqconk64,_retargs_getqconk64 = self.__obj.getqconk64_iOOO_5(k,memview_qcsubi,memview_qcsubj,memview_qcval)
      if _res_getqconk64 != 0:
        _,_msg_getqconk64 = self.__getlasterror(_res_getqconk64)
        raise Error(rescode(_res_getqconk64),_msg_getqconk64)
      else:
        (numqcnz) = _retargs_getqconk64
      if copyback_qcsubi:
        for __tmp_320 in range(len(qcsubi)): qcsubi[__tmp_320] = qcsubi_[__tmp_320]
      if copyback_qcsubj:
        for __tmp_323 in range(len(qcsubj)): qcsubj[__tmp_323] = qcsubj_[__tmp_323]
      if copyback_qcval:
        for __tmp_326 in range(len(qcval)): qcval[__tmp_326] = qcval_[__tmp_326]
      return (numqcnz)
    def __getqconk64_iOOO_2(self,k):
      qcsubi_ = bytearray(0)
      qcsubj_ = bytearray(0)
      qcval_ = bytearray(0)
      _res_getqconk64,_retargs_getqconk64 = self.__obj.getqconk64_iOOO_2(k,qcsubi_,qcsubj_,qcval_)
      if _res_getqconk64 != 0:
        _,_msg_getqconk64 = self.__getlasterror(_res_getqconk64)
        raise Error(rescode(_res_getqconk64),_msg_getqconk64)
      else:
        (numqcnz) = _retargs_getqconk64
      qcsubi = array.array("i")
      qcsubi.frombytes(qcsubi_)
      qcsubj = array.array("i")
      qcsubj.frombytes(qcsubj_)
      qcval = array.array("d")
      qcval.frombytes(qcval_)
      return (numqcnz,qcsubi,qcsubj,qcval)
    def getqconk(self,*args,**kwds):
      """
      Obtains all the quadratic terms in a constraint.
    
      getqconk(k,qcsubi,qcsubj,qcval) -> (numqcnz)
      getqconk(k) -> (numqcnz,qcsubi,qcsubj,qcval)
        [k : int32]  Which constraint.  
        [numqcnz : int64]  Number of quadratic terms.  
        [qcsubi : array(int32)]  Row subscripts for quadratic constraint matrix.  
        [qcsubj : array(int32)]  Column subscripts for quadratic constraint matrix.  
        [qcval : array(float64)]  Quadratic constraint coefficient values.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getqconk64_iOOO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getqconk64_iOOO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getqobj64_OOO_4(self,qosubi,qosubj,qoval):
      if qosubi is None:
        raise TypeError("Argument qosubi may not be None")
      copyback_qosubi = False
      if qosubi is None:
        qosubi_ = None
        memview_qosubi = None
      else:
        try:
          memview_qosubi = memoryview(qosubi)
        except TypeError:
          try:
            _tmparray_qosubi = array.array("i",[0 for _ in range(len(qosubi))])
          except TypeError:
            raise TypeError("Argument qosubi has wrong type") from None
          else:
            memview_qosubi = memoryview(_tmparray_qosubi)
            copyback_qosubi = True
            qosubi_ = _tmparray_qosubi
        else:
          if memview_qosubi.ndim != 1:
            raise TypeError("Argument qosubi must be one-dimensional")
          if memview_qosubi.format != "i":
            _tmparray_qosubi = array.array("i",qosubi)
            memview_qosubi = memoryview(_tmparray_qosubi)
            copyback_qosubi = True
            qosubi_ = _tmparray_qosubi
      if qosubj is None:
        raise TypeError("Argument qosubj may not be None")
      copyback_qosubj = False
      if qosubj is None:
        qosubj_ = None
        memview_qosubj = None
      else:
        try:
          memview_qosubj = memoryview(qosubj)
        except TypeError:
          try:
            _tmparray_qosubj = array.array("i",[0 for _ in range(len(qosubj))])
          except TypeError:
            raise TypeError("Argument qosubj has wrong type") from None
          else:
            memview_qosubj = memoryview(_tmparray_qosubj)
            copyback_qosubj = True
            qosubj_ = _tmparray_qosubj
        else:
          if memview_qosubj.ndim != 1:
            raise TypeError("Argument qosubj must be one-dimensional")
          if memview_qosubj.format != "i":
            _tmparray_qosubj = array.array("i",qosubj)
            memview_qosubj = memoryview(_tmparray_qosubj)
            copyback_qosubj = True
            qosubj_ = _tmparray_qosubj
      if qoval is None:
        raise TypeError("Argument qoval may not be None")
      copyback_qoval = False
      if qoval is None:
        qoval_ = None
        memview_qoval = None
      else:
        try:
          memview_qoval = memoryview(qoval)
        except TypeError:
          try:
            _tmparray_qoval = array.array("d",[0 for _ in range(len(qoval))])
          except TypeError:
            raise TypeError("Argument qoval has wrong type") from None
          else:
            memview_qoval = memoryview(_tmparray_qoval)
            copyback_qoval = True
            qoval_ = _tmparray_qoval
        else:
          if memview_qoval.ndim != 1:
            raise TypeError("Argument qoval must be one-dimensional")
          if memview_qoval.format != "d":
            _tmparray_qoval = array.array("d",qoval)
            memview_qoval = memoryview(_tmparray_qoval)
            copyback_qoval = True
            qoval_ = _tmparray_qoval
      _res_getqobj64,_retargs_getqobj64 = self.__obj.getqobj64_OOO_4(memview_qosubi,memview_qosubj,memview_qoval)
      if _res_getqobj64 != 0:
        _,_msg_getqobj64 = self.__getlasterror(_res_getqobj64)
        raise Error(rescode(_res_getqobj64),_msg_getqobj64)
      else:
        (numqonz) = _retargs_getqobj64
      if copyback_qosubi:
        for __tmp_340 in range(len(qosubi)): qosubi[__tmp_340] = qosubi_[__tmp_340]
      if copyback_qosubj:
        for __tmp_341 in range(len(qosubj)): qosubj[__tmp_341] = qosubj_[__tmp_341]
      if copyback_qoval:
        for __tmp_342 in range(len(qoval)): qoval[__tmp_342] = qoval_[__tmp_342]
      return (numqonz)
    def __getqobj64_OOO_1(self):
      qosubi_ = bytearray(0)
      qosubj_ = bytearray(0)
      qoval_ = bytearray(0)
      _res_getqobj64,_retargs_getqobj64 = self.__obj.getqobj64_OOO_1(qosubi_,qosubj_,qoval_)
      if _res_getqobj64 != 0:
        _,_msg_getqobj64 = self.__getlasterror(_res_getqobj64)
        raise Error(rescode(_res_getqobj64),_msg_getqobj64)
      else:
        (numqonz) = _retargs_getqobj64
      qosubi = array.array("i")
      qosubi.frombytes(qosubi_)
      qosubj = array.array("i")
      qosubj.frombytes(qosubj_)
      qoval = array.array("d")
      qoval.frombytes(qoval_)
      return (numqonz,qosubi,qosubj,qoval)
    def getqobj(self,*args,**kwds):
      """
      Obtains all the quadratic terms in the objective.
    
      getqobj(qosubi,qosubj,qoval) -> (numqonz)
      getqobj() -> (numqonz,qosubi,qosubj,qoval)
        [numqonz : int64]  Number of non-zero elements in the quadratic objective terms.  
        [qosubi : array(int32)]  Row subscripts for quadratic objective coefficients.  
        [qosubj : array(int32)]  Column subscripts for quadratic objective coefficients.  
        [qoval : array(float64)]  Quadratic objective coefficient values.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getqobj64_OOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getqobj64_OOO_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getqobjij_ii_3(self,i,j):
      _res_getqobjij,_retargs_getqobjij = self.__obj.getqobjij_ii_3(i,j)
      if _res_getqobjij != 0:
        _,_msg_getqobjij = self.__getlasterror(_res_getqobjij)
        raise Error(rescode(_res_getqobjij),_msg_getqobjij)
      else:
        (qoij) = _retargs_getqobjij
      return (qoij)
    def getqobjij(self,*args,**kwds):
      """
      Obtains one coefficient from the quadratic term of the objective
    
      getqobjij(i,j) -> (qoij)
        [i : int32]  Row index of the coefficient.  
        [j : int32]  Column index of coefficient.  
        [qoij : float64]  The required coefficient.  
      """
      return self.__getqobjij_ii_3(*args,**kwds)
    def __getsolution_iOOOOOOOOOOO_13(self,whichsol,skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx):
      if skc is None:
        skc_ = None
      else:
        # o
        _tmparray_skc_ = array.array("i",[0 for _ in range(len(skc))])
        skc_ = memoryview(_tmparray_skc_)
      if skx is None:
        skx_ = None
      else:
        # o
        _tmparray_skx_ = array.array("i",[0 for _ in range(len(skx))])
        skx_ = memoryview(_tmparray_skx_)
      if skn is None:
        skn_ = None
      else:
        # o
        _tmparray_skn_ = array.array("i",[0 for _ in range(len(skn))])
        skn_ = memoryview(_tmparray_skn_)
      copyback_xc = False
      if xc is None:
        xc_ = None
        memview_xc = None
      else:
        try:
          memview_xc = memoryview(xc)
        except TypeError:
          try:
            _tmparray_xc = array.array("d",[0 for _ in range(len(xc))])
          except TypeError:
            raise TypeError("Argument xc has wrong type") from None
          else:
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
        else:
          if memview_xc.ndim != 1:
            raise TypeError("Argument xc must be one-dimensional")
          if memview_xc.format != "d":
            _tmparray_xc = array.array("d",xc)
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
      copyback_xx = False
      if xx is None:
        xx_ = None
        memview_xx = None
      else:
        try:
          memview_xx = memoryview(xx)
        except TypeError:
          try:
            _tmparray_xx = array.array("d",[0 for _ in range(len(xx))])
          except TypeError:
            raise TypeError("Argument xx has wrong type") from None
          else:
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
        else:
          if memview_xx.ndim != 1:
            raise TypeError("Argument xx must be one-dimensional")
          if memview_xx.format != "d":
            _tmparray_xx = array.array("d",xx)
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
      copyback_y = False
      if y is None:
        y_ = None
        memview_y = None
      else:
        try:
          memview_y = memoryview(y)
        except TypeError:
          try:
            _tmparray_y = array.array("d",[0 for _ in range(len(y))])
          except TypeError:
            raise TypeError("Argument y has wrong type") from None
          else:
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
        else:
          if memview_y.ndim != 1:
            raise TypeError("Argument y must be one-dimensional")
          if memview_y.format != "d":
            _tmparray_y = array.array("d",y)
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
      copyback_slc = False
      if slc is None:
        slc_ = None
        memview_slc = None
      else:
        try:
          memview_slc = memoryview(slc)
        except TypeError:
          try:
            _tmparray_slc = array.array("d",[0 for _ in range(len(slc))])
          except TypeError:
            raise TypeError("Argument slc has wrong type") from None
          else:
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
        else:
          if memview_slc.ndim != 1:
            raise TypeError("Argument slc must be one-dimensional")
          if memview_slc.format != "d":
            _tmparray_slc = array.array("d",slc)
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
      copyback_suc = False
      if suc is None:
        suc_ = None
        memview_suc = None
      else:
        try:
          memview_suc = memoryview(suc)
        except TypeError:
          try:
            _tmparray_suc = array.array("d",[0 for _ in range(len(suc))])
          except TypeError:
            raise TypeError("Argument suc has wrong type") from None
          else:
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
        else:
          if memview_suc.ndim != 1:
            raise TypeError("Argument suc must be one-dimensional")
          if memview_suc.format != "d":
            _tmparray_suc = array.array("d",suc)
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
      copyback_slx = False
      if slx is None:
        slx_ = None
        memview_slx = None
      else:
        try:
          memview_slx = memoryview(slx)
        except TypeError:
          try:
            _tmparray_slx = array.array("d",[0 for _ in range(len(slx))])
          except TypeError:
            raise TypeError("Argument slx has wrong type") from None
          else:
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
        else:
          if memview_slx.ndim != 1:
            raise TypeError("Argument slx must be one-dimensional")
          if memview_slx.format != "d":
            _tmparray_slx = array.array("d",slx)
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
      copyback_sux = False
      if sux is None:
        sux_ = None
        memview_sux = None
      else:
        try:
          memview_sux = memoryview(sux)
        except TypeError:
          try:
            _tmparray_sux = array.array("d",[0 for _ in range(len(sux))])
          except TypeError:
            raise TypeError("Argument sux has wrong type") from None
          else:
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
        else:
          if memview_sux.ndim != 1:
            raise TypeError("Argument sux must be one-dimensional")
          if memview_sux.format != "d":
            _tmparray_sux = array.array("d",sux)
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
      copyback_snx = False
      if snx is None:
        snx_ = None
        memview_snx = None
      else:
        try:
          memview_snx = memoryview(snx)
        except TypeError:
          try:
            _tmparray_snx = array.array("d",[0 for _ in range(len(snx))])
          except TypeError:
            raise TypeError("Argument snx has wrong type") from None
          else:
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
        else:
          if memview_snx.ndim != 1:
            raise TypeError("Argument snx must be one-dimensional")
          if memview_snx.format != "d":
            _tmparray_snx = array.array("d",snx)
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
      _res_getsolution,_retargs_getsolution = self.__obj.getsolution_iOOOOOOOOOOO_13(whichsol,skc_,skx_,skn_,memview_xc,memview_xx,memview_y,memview_slc,memview_suc,memview_slx,memview_sux,memview_snx)
      if _res_getsolution != 0:
        _,_msg_getsolution = self.__getlasterror(_res_getsolution)
        raise Error(rescode(_res_getsolution),_msg_getsolution)
      else:
        (problemsta,solutionsta) = _retargs_getsolution
      for __tmp_350 in range(len(skc)): skc[__tmp_350] = stakey(skc_[__tmp_350])
      for __tmp_353 in range(len(skx)): skx[__tmp_353] = stakey(skx_[__tmp_353])
      for __tmp_356 in range(len(skn)): skn[__tmp_356] = stakey(skn_[__tmp_356])
      if copyback_xc:
        for __tmp_359 in range(len(xc)): xc[__tmp_359] = xc_[__tmp_359]
      if copyback_xx:
        for __tmp_362 in range(len(xx)): xx[__tmp_362] = xx_[__tmp_362]
      if copyback_y:
        for __tmp_365 in range(len(y)): y[__tmp_365] = y_[__tmp_365]
      if copyback_slc:
        for __tmp_368 in range(len(slc)): slc[__tmp_368] = slc_[__tmp_368]
      if copyback_suc:
        for __tmp_371 in range(len(suc)): suc[__tmp_371] = suc_[__tmp_371]
      if copyback_slx:
        for __tmp_374 in range(len(slx)): slx[__tmp_374] = slx_[__tmp_374]
      if copyback_sux:
        for __tmp_377 in range(len(sux)): sux[__tmp_377] = sux_[__tmp_377]
      if copyback_snx:
        for __tmp_380 in range(len(snx)): snx[__tmp_380] = snx_[__tmp_380]
      return (prosta(problemsta),solsta(solutionsta))
    def __getsolution_iOOOOOOOOOOO_2(self,whichsol):
      skc_ = bytearray(0)
      skx_ = bytearray(0)
      skn_ = bytearray(0)
      xc_ = bytearray(0)
      xx_ = bytearray(0)
      y_ = bytearray(0)
      slc_ = bytearray(0)
      suc_ = bytearray(0)
      slx_ = bytearray(0)
      sux_ = bytearray(0)
      snx_ = bytearray(0)
      _res_getsolution,_retargs_getsolution = self.__obj.getsolution_iOOOOOOOOOOO_2(whichsol,skc_,skx_,skn_,xc_,xx_,y_,slc_,suc_,slx_,sux_,snx_)
      if _res_getsolution != 0:
        _,_msg_getsolution = self.__getlasterror(_res_getsolution)
        raise Error(rescode(_res_getsolution),_msg_getsolution)
      else:
        (problemsta,solutionsta) = _retargs_getsolution
      skc_ints = array.array("i")
      skc_ints.frombytes(skc_)
      skc = [ stakey(__tmp_383) for __tmp_383 in skc_ints ]
      skx_ints = array.array("i")
      skx_ints.frombytes(skx_)
      skx = [ stakey(__tmp_386) for __tmp_386 in skx_ints ]
      skn_ints = array.array("i")
      skn_ints.frombytes(skn_)
      skn = [ stakey(__tmp_389) for __tmp_389 in skn_ints ]
      xc = array.array("d")
      xc.frombytes(xc_)
      xx = array.array("d")
      xx.frombytes(xx_)
      y = array.array("d")
      y.frombytes(y_)
      slc = array.array("d")
      slc.frombytes(slc_)
      suc = array.array("d")
      suc.frombytes(suc_)
      slx = array.array("d")
      slx.frombytes(slx_)
      sux = array.array("d")
      sux.frombytes(sux_)
      snx = array.array("d")
      snx.frombytes(snx_)
      return (prosta(problemsta),solsta(solutionsta),skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx)
    def getsolution(self,*args,**kwds):
      """
      Obtains the complete solution.
    
      getsolution(whichsol,
                  skc,
                  skx,
                  skn,
                  xc,
                  xx,
                  y,
                  slc,
                  suc,
                  slx,
                  sux,
                  snx) -> (problemsta,solutionsta)
      getsolution(whichsol) -> 
                 (problemsta,
                  solutionsta,
                  skc,
                  skx,
                  skn,
                  xc,
                  xx,
                  y,
                  slc,
                  suc,
                  slx,
                  sux,
                  snx)
        [problemsta : mosek.prosta]  Problem status.  
        [skc : array(mosek.stakey)]  Status keys for the constraints.  
        [skn : array(mosek.stakey)]  Status keys for the conic constraints.  
        [skx : array(mosek.stakey)]  Status keys for the variables.  
        [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
        [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
        [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
        [solutionsta : mosek.solsta]  Solution status.  
        [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
        [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [xc : array(float64)]  Primal constraint solution.  
        [xx : array(float64)]  Primal variable solution.  
        [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 13: return self.__getsolution_iOOOOOOOOOOO_13(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getsolution_iOOOOOOOOOOO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getsolutionnew_iOOOOOOOOOOOO_14(self,whichsol,skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx,doty):
      if skc is None:
        skc_ = None
      else:
        # o
        _tmparray_skc_ = array.array("i",[0 for _ in range(len(skc))])
        skc_ = memoryview(_tmparray_skc_)
      if skx is None:
        skx_ = None
      else:
        # o
        _tmparray_skx_ = array.array("i",[0 for _ in range(len(skx))])
        skx_ = memoryview(_tmparray_skx_)
      if skn is None:
        skn_ = None
      else:
        # o
        _tmparray_skn_ = array.array("i",[0 for _ in range(len(skn))])
        skn_ = memoryview(_tmparray_skn_)
      copyback_xc = False
      if xc is None:
        xc_ = None
        memview_xc = None
      else:
        try:
          memview_xc = memoryview(xc)
        except TypeError:
          try:
            _tmparray_xc = array.array("d",[0 for _ in range(len(xc))])
          except TypeError:
            raise TypeError("Argument xc has wrong type") from None
          else:
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
        else:
          if memview_xc.ndim != 1:
            raise TypeError("Argument xc must be one-dimensional")
          if memview_xc.format != "d":
            _tmparray_xc = array.array("d",xc)
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
      copyback_xx = False
      if xx is None:
        xx_ = None
        memview_xx = None
      else:
        try:
          memview_xx = memoryview(xx)
        except TypeError:
          try:
            _tmparray_xx = array.array("d",[0 for _ in range(len(xx))])
          except TypeError:
            raise TypeError("Argument xx has wrong type") from None
          else:
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
        else:
          if memview_xx.ndim != 1:
            raise TypeError("Argument xx must be one-dimensional")
          if memview_xx.format != "d":
            _tmparray_xx = array.array("d",xx)
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
      copyback_y = False
      if y is None:
        y_ = None
        memview_y = None
      else:
        try:
          memview_y = memoryview(y)
        except TypeError:
          try:
            _tmparray_y = array.array("d",[0 for _ in range(len(y))])
          except TypeError:
            raise TypeError("Argument y has wrong type") from None
          else:
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
        else:
          if memview_y.ndim != 1:
            raise TypeError("Argument y must be one-dimensional")
          if memview_y.format != "d":
            _tmparray_y = array.array("d",y)
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
      copyback_slc = False
      if slc is None:
        slc_ = None
        memview_slc = None
      else:
        try:
          memview_slc = memoryview(slc)
        except TypeError:
          try:
            _tmparray_slc = array.array("d",[0 for _ in range(len(slc))])
          except TypeError:
            raise TypeError("Argument slc has wrong type") from None
          else:
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
        else:
          if memview_slc.ndim != 1:
            raise TypeError("Argument slc must be one-dimensional")
          if memview_slc.format != "d":
            _tmparray_slc = array.array("d",slc)
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
      copyback_suc = False
      if suc is None:
        suc_ = None
        memview_suc = None
      else:
        try:
          memview_suc = memoryview(suc)
        except TypeError:
          try:
            _tmparray_suc = array.array("d",[0 for _ in range(len(suc))])
          except TypeError:
            raise TypeError("Argument suc has wrong type") from None
          else:
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
        else:
          if memview_suc.ndim != 1:
            raise TypeError("Argument suc must be one-dimensional")
          if memview_suc.format != "d":
            _tmparray_suc = array.array("d",suc)
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
      copyback_slx = False
      if slx is None:
        slx_ = None
        memview_slx = None
      else:
        try:
          memview_slx = memoryview(slx)
        except TypeError:
          try:
            _tmparray_slx = array.array("d",[0 for _ in range(len(slx))])
          except TypeError:
            raise TypeError("Argument slx has wrong type") from None
          else:
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
        else:
          if memview_slx.ndim != 1:
            raise TypeError("Argument slx must be one-dimensional")
          if memview_slx.format != "d":
            _tmparray_slx = array.array("d",slx)
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
      copyback_sux = False
      if sux is None:
        sux_ = None
        memview_sux = None
      else:
        try:
          memview_sux = memoryview(sux)
        except TypeError:
          try:
            _tmparray_sux = array.array("d",[0 for _ in range(len(sux))])
          except TypeError:
            raise TypeError("Argument sux has wrong type") from None
          else:
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
        else:
          if memview_sux.ndim != 1:
            raise TypeError("Argument sux must be one-dimensional")
          if memview_sux.format != "d":
            _tmparray_sux = array.array("d",sux)
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
      copyback_snx = False
      if snx is None:
        snx_ = None
        memview_snx = None
      else:
        try:
          memview_snx = memoryview(snx)
        except TypeError:
          try:
            _tmparray_snx = array.array("d",[0 for _ in range(len(snx))])
          except TypeError:
            raise TypeError("Argument snx has wrong type") from None
          else:
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
        else:
          if memview_snx.ndim != 1:
            raise TypeError("Argument snx must be one-dimensional")
          if memview_snx.format != "d":
            _tmparray_snx = array.array("d",snx)
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
      copyback_doty = False
      if doty is None:
        doty_ = None
        memview_doty = None
      else:
        try:
          memview_doty = memoryview(doty)
        except TypeError:
          try:
            _tmparray_doty = array.array("d",[0 for _ in range(len(doty))])
          except TypeError:
            raise TypeError("Argument doty has wrong type") from None
          else:
            memview_doty = memoryview(_tmparray_doty)
            copyback_doty = True
            doty_ = _tmparray_doty
        else:
          if memview_doty.ndim != 1:
            raise TypeError("Argument doty must be one-dimensional")
          if memview_doty.format != "d":
            _tmparray_doty = array.array("d",doty)
            memview_doty = memoryview(_tmparray_doty)
            copyback_doty = True
            doty_ = _tmparray_doty
      _res_getsolutionnew,_retargs_getsolutionnew = self.__obj.getsolutionnew_iOOOOOOOOOOOO_14(whichsol,skc_,skx_,skn_,memview_xc,memview_xx,memview_y,memview_slc,memview_suc,memview_slx,memview_sux,memview_snx,memview_doty)
      if _res_getsolutionnew != 0:
        _,_msg_getsolutionnew = self.__getlasterror(_res_getsolutionnew)
        raise Error(rescode(_res_getsolutionnew),_msg_getsolutionnew)
      else:
        (problemsta,solutionsta) = _retargs_getsolutionnew
      for __tmp_416 in range(len(skc)): skc[__tmp_416] = stakey(skc_[__tmp_416])
      for __tmp_419 in range(len(skx)): skx[__tmp_419] = stakey(skx_[__tmp_419])
      for __tmp_422 in range(len(skn)): skn[__tmp_422] = stakey(skn_[__tmp_422])
      if copyback_xc:
        for __tmp_425 in range(len(xc)): xc[__tmp_425] = xc_[__tmp_425]
      if copyback_xx:
        for __tmp_428 in range(len(xx)): xx[__tmp_428] = xx_[__tmp_428]
      if copyback_y:
        for __tmp_431 in range(len(y)): y[__tmp_431] = y_[__tmp_431]
      if copyback_slc:
        for __tmp_434 in range(len(slc)): slc[__tmp_434] = slc_[__tmp_434]
      if copyback_suc:
        for __tmp_437 in range(len(suc)): suc[__tmp_437] = suc_[__tmp_437]
      if copyback_slx:
        for __tmp_440 in range(len(slx)): slx[__tmp_440] = slx_[__tmp_440]
      if copyback_sux:
        for __tmp_443 in range(len(sux)): sux[__tmp_443] = sux_[__tmp_443]
      if copyback_snx:
        for __tmp_446 in range(len(snx)): snx[__tmp_446] = snx_[__tmp_446]
      if copyback_doty:
        for __tmp_449 in range(len(doty)): doty[__tmp_449] = doty_[__tmp_449]
      return (prosta(problemsta),solsta(solutionsta))
    def __getsolutionnew_iOOOOOOOOOOOO_2(self,whichsol):
      skc_ = bytearray(0)
      skx_ = bytearray(0)
      skn_ = bytearray(0)
      xc_ = bytearray(0)
      xx_ = bytearray(0)
      y_ = bytearray(0)
      slc_ = bytearray(0)
      suc_ = bytearray(0)
      slx_ = bytearray(0)
      sux_ = bytearray(0)
      snx_ = bytearray(0)
      doty_ = bytearray(0)
      _res_getsolutionnew,_retargs_getsolutionnew = self.__obj.getsolutionnew_iOOOOOOOOOOOO_2(whichsol,skc_,skx_,skn_,xc_,xx_,y_,slc_,suc_,slx_,sux_,snx_,doty_)
      if _res_getsolutionnew != 0:
        _,_msg_getsolutionnew = self.__getlasterror(_res_getsolutionnew)
        raise Error(rescode(_res_getsolutionnew),_msg_getsolutionnew)
      else:
        (problemsta,solutionsta) = _retargs_getsolutionnew
      skc_ints = array.array("i")
      skc_ints.frombytes(skc_)
      skc = [ stakey(__tmp_452) for __tmp_452 in skc_ints ]
      skx_ints = array.array("i")
      skx_ints.frombytes(skx_)
      skx = [ stakey(__tmp_455) for __tmp_455 in skx_ints ]
      skn_ints = array.array("i")
      skn_ints.frombytes(skn_)
      skn = [ stakey(__tmp_458) for __tmp_458 in skn_ints ]
      xc = array.array("d")
      xc.frombytes(xc_)
      xx = array.array("d")
      xx.frombytes(xx_)
      y = array.array("d")
      y.frombytes(y_)
      slc = array.array("d")
      slc.frombytes(slc_)
      suc = array.array("d")
      suc.frombytes(suc_)
      slx = array.array("d")
      slx.frombytes(slx_)
      sux = array.array("d")
      sux.frombytes(sux_)
      snx = array.array("d")
      snx.frombytes(snx_)
      doty = array.array("d")
      doty.frombytes(doty_)
      return (prosta(problemsta),solsta(solutionsta),skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx,doty)
    def getsolutionnew(self,*args,**kwds):
      """
      Obtains the complete solution.
    
      getsolutionnew(whichsol,
                     skc,
                     skx,
                     skn,
                     xc,
                     xx,
                     y,
                     slc,
                     suc,
                     slx,
                     sux,
                     snx,
                     doty) -> (problemsta,solutionsta)
      getsolutionnew(whichsol) -> 
                    (problemsta,
                     solutionsta,
                     skc,
                     skx,
                     skn,
                     xc,
                     xx,
                     y,
                     slc,
                     suc,
                     slx,
                     sux,
                     snx,
                     doty)
        [doty : array(float64)]  Dual variables corresponding to affine conic constraints.  
        [problemsta : mosek.prosta]  Problem status.  
        [skc : array(mosek.stakey)]  Status keys for the constraints.  
        [skn : array(mosek.stakey)]  Status keys for the conic constraints.  
        [skx : array(mosek.stakey)]  Status keys for the variables.  
        [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
        [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
        [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
        [solutionsta : mosek.solsta]  Solution status.  
        [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
        [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [xc : array(float64)]  Primal constraint solution.  
        [xx : array(float64)]  Primal variable solution.  
        [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 14: return self.__getsolutionnew_iOOOOOOOOOOOO_14(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getsolutionnew_iOOOOOOOOOOOO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getsolsta_i_2(self,whichsol):
      _res_getsolsta,_retargs_getsolsta = self.__obj.getsolsta_i_2(whichsol)
      if _res_getsolsta != 0:
        _,_msg_getsolsta = self.__getlasterror(_res_getsolsta)
        raise Error(rescode(_res_getsolsta),_msg_getsolsta)
      else:
        (solutionsta) = _retargs_getsolsta
      return (solsta(solutionsta))
    def getsolsta(self,*args,**kwds):
      """
      Obtains the solution status.
    
      getsolsta(whichsol) -> (solutionsta)
        [solutionsta : mosek.solsta]  Solution status.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__getsolsta_i_2(*args,**kwds)
    def __getprosta_i_2(self,whichsol):
      _res_getprosta,_retargs_getprosta = self.__obj.getprosta_i_2(whichsol)
      if _res_getprosta != 0:
        _,_msg_getprosta = self.__getlasterror(_res_getprosta)
        raise Error(rescode(_res_getprosta),_msg_getprosta)
      else:
        (problemsta) = _retargs_getprosta
      return (prosta(problemsta))
    def getprosta(self,*args,**kwds):
      """
      Obtains the problem status.
    
      getprosta(whichsol) -> (problemsta)
        [problemsta : mosek.prosta]  Problem status.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__getprosta_i_2(*args,**kwds)
    def __getskc_iO_3(self,whichsol,skc):
      if skc is None:
        skc_ = None
      else:
        # o
        _tmparray_skc_ = array.array("i",[0 for _ in range(len(skc))])
        skc_ = memoryview(_tmparray_skc_)
      _res_getskc,_retargs_getskc = self.__obj.getskc_iO_3(whichsol,skc_)
      if _res_getskc != 0:
        _,_msg_getskc = self.__getlasterror(_res_getskc)
        raise Error(rescode(_res_getskc),_msg_getskc)
      for __tmp_488 in range(len(skc)): skc[__tmp_488] = stakey(skc_[__tmp_488])
    def __getskc_iO_2(self,whichsol):
      skc_ = bytearray(0)
      _res_getskc,_retargs_getskc = self.__obj.getskc_iO_2(whichsol,skc_)
      if _res_getskc != 0:
        _,_msg_getskc = self.__getlasterror(_res_getskc)
        raise Error(rescode(_res_getskc),_msg_getskc)
      skc_ints = array.array("i")
      skc_ints.frombytes(skc_)
      skc = [ stakey(__tmp_491) for __tmp_491 in skc_ints ]
      return (skc)
    def getskc(self,*args,**kwds):
      """
      Obtains the status keys for the constraints.
    
      getskc(whichsol,skc)
      getskc(whichsol) -> (skc)
        [skc : array(mosek.stakey)]  Status keys for the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getskc_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getskc_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getskx_iO_3(self,whichsol,skx):
      if skx is None:
        skx_ = None
      else:
        # o
        _tmparray_skx_ = array.array("i",[0 for _ in range(len(skx))])
        skx_ = memoryview(_tmparray_skx_)
      _res_getskx,_retargs_getskx = self.__obj.getskx_iO_3(whichsol,skx_)
      if _res_getskx != 0:
        _,_msg_getskx = self.__getlasterror(_res_getskx)
        raise Error(rescode(_res_getskx),_msg_getskx)
      for __tmp_494 in range(len(skx)): skx[__tmp_494] = stakey(skx_[__tmp_494])
    def __getskx_iO_2(self,whichsol):
      skx_ = bytearray(0)
      _res_getskx,_retargs_getskx = self.__obj.getskx_iO_2(whichsol,skx_)
      if _res_getskx != 0:
        _,_msg_getskx = self.__getlasterror(_res_getskx)
        raise Error(rescode(_res_getskx),_msg_getskx)
      skx_ints = array.array("i")
      skx_ints.frombytes(skx_)
      skx = [ stakey(__tmp_497) for __tmp_497 in skx_ints ]
      return (skx)
    def getskx(self,*args,**kwds):
      """
      Obtains the status keys for the scalar variables.
    
      getskx(whichsol,skx)
      getskx(whichsol) -> (skx)
        [skx : array(mosek.stakey)]  Status keys for the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getskx_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getskx_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getskn_iO_3(self,whichsol,skn):
      if skn is None:
        skn_ = None
      else:
        # o
        _tmparray_skn_ = array.array("i",[0 for _ in range(len(skn))])
        skn_ = memoryview(_tmparray_skn_)
      _res_getskn,_retargs_getskn = self.__obj.getskn_iO_3(whichsol,skn_)
      if _res_getskn != 0:
        _,_msg_getskn = self.__getlasterror(_res_getskn)
        raise Error(rescode(_res_getskn),_msg_getskn)
      for __tmp_500 in range(len(skn)): skn[__tmp_500] = stakey(skn_[__tmp_500])
    def __getskn_iO_2(self,whichsol):
      skn_ = bytearray(0)
      _res_getskn,_retargs_getskn = self.__obj.getskn_iO_2(whichsol,skn_)
      if _res_getskn != 0:
        _,_msg_getskn = self.__getlasterror(_res_getskn)
        raise Error(rescode(_res_getskn),_msg_getskn)
      skn_ints = array.array("i")
      skn_ints.frombytes(skn_)
      skn = [ stakey(__tmp_503) for __tmp_503 in skn_ints ]
      return (skn)
    def getskn(self,*args,**kwds):
      """
      Obtains the status keys for the conic constraints.
    
      getskn(whichsol,skn)
      getskn(whichsol) -> (skn)
        [skn : array(mosek.stakey)]  Status keys for the conic constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getskn_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getskn_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getxc_iO_3(self,whichsol,xc):
      if xc is None:
        raise TypeError("Argument xc may not be None")
      copyback_xc = False
      if xc is None:
        xc_ = None
        memview_xc = None
      else:
        try:
          memview_xc = memoryview(xc)
        except TypeError:
          try:
            _tmparray_xc = array.array("d",[0 for _ in range(len(xc))])
          except TypeError:
            raise TypeError("Argument xc has wrong type") from None
          else:
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
        else:
          if memview_xc.ndim != 1:
            raise TypeError("Argument xc must be one-dimensional")
          if memview_xc.format != "d":
            _tmparray_xc = array.array("d",xc)
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
      _res_getxc,_retargs_getxc = self.__obj.getxc_iO_3(whichsol,memview_xc)
      if _res_getxc != 0:
        _,_msg_getxc = self.__getlasterror(_res_getxc)
        raise Error(rescode(_res_getxc),_msg_getxc)
      if copyback_xc:
        for __tmp_506 in range(len(xc)): xc[__tmp_506] = xc_[__tmp_506]
    def __getxc_iO_2(self,whichsol):
      xc_ = bytearray(0)
      _res_getxc,_retargs_getxc = self.__obj.getxc_iO_2(whichsol,xc_)
      if _res_getxc != 0:
        _,_msg_getxc = self.__getlasterror(_res_getxc)
        raise Error(rescode(_res_getxc),_msg_getxc)
      xc = array.array("d")
      xc.frombytes(xc_)
      return (xc)
    def getxc(self,*args,**kwds):
      """
      Obtains the xc vector for a solution.
    
      getxc(whichsol,xc)
      getxc(whichsol) -> (xc)
        [whichsol : mosek.soltype]  Selects a solution.  
        [xc : array(float64)]  Primal constraint solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getxc_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getxc_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getxx_iO_3(self,whichsol,xx):
      if xx is None:
        raise TypeError("Argument xx may not be None")
      copyback_xx = False
      if xx is None:
        xx_ = None
        memview_xx = None
      else:
        try:
          memview_xx = memoryview(xx)
        except TypeError:
          try:
            _tmparray_xx = array.array("d",[0 for _ in range(len(xx))])
          except TypeError:
            raise TypeError("Argument xx has wrong type") from None
          else:
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
        else:
          if memview_xx.ndim != 1:
            raise TypeError("Argument xx must be one-dimensional")
          if memview_xx.format != "d":
            _tmparray_xx = array.array("d",xx)
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
      _res_getxx,_retargs_getxx = self.__obj.getxx_iO_3(whichsol,memview_xx)
      if _res_getxx != 0:
        _,_msg_getxx = self.__getlasterror(_res_getxx)
        raise Error(rescode(_res_getxx),_msg_getxx)
      if copyback_xx:
        for __tmp_512 in range(len(xx)): xx[__tmp_512] = xx_[__tmp_512]
    def __getxx_iO_2(self,whichsol):
      xx_ = bytearray(0)
      _res_getxx,_retargs_getxx = self.__obj.getxx_iO_2(whichsol,xx_)
      if _res_getxx != 0:
        _,_msg_getxx = self.__getlasterror(_res_getxx)
        raise Error(rescode(_res_getxx),_msg_getxx)
      xx = array.array("d")
      xx.frombytes(xx_)
      return (xx)
    def getxx(self,*args,**kwds):
      """
      Obtains the xx vector for a solution.
    
      getxx(whichsol,xx)
      getxx(whichsol) -> (xx)
        [whichsol : mosek.soltype]  Selects a solution.  
        [xx : array(float64)]  Primal variable solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getxx_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getxx_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __gety_iO_3(self,whichsol,y):
      if y is None:
        raise TypeError("Argument y may not be None")
      copyback_y = False
      if y is None:
        y_ = None
        memview_y = None
      else:
        try:
          memview_y = memoryview(y)
        except TypeError:
          try:
            _tmparray_y = array.array("d",[0 for _ in range(len(y))])
          except TypeError:
            raise TypeError("Argument y has wrong type") from None
          else:
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
        else:
          if memview_y.ndim != 1:
            raise TypeError("Argument y must be one-dimensional")
          if memview_y.format != "d":
            _tmparray_y = array.array("d",y)
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
      _res_gety,_retargs_gety = self.__obj.gety_iO_3(whichsol,memview_y)
      if _res_gety != 0:
        _,_msg_gety = self.__getlasterror(_res_gety)
        raise Error(rescode(_res_gety),_msg_gety)
      if copyback_y:
        for __tmp_518 in range(len(y)): y[__tmp_518] = y_[__tmp_518]
    def __gety_iO_2(self,whichsol):
      y_ = bytearray(0)
      _res_gety,_retargs_gety = self.__obj.gety_iO_2(whichsol,y_)
      if _res_gety != 0:
        _,_msg_gety = self.__getlasterror(_res_gety)
        raise Error(rescode(_res_gety),_msg_gety)
      y = array.array("d")
      y.frombytes(y_)
      return (y)
    def gety(self,*args,**kwds):
      """
      Obtains the y vector for a solution.
    
      gety(whichsol,y)
      gety(whichsol) -> (y)
        [whichsol : mosek.soltype]  Selects a solution.  
        [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__gety_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__gety_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getslc_iO_3(self,whichsol,slc):
      if slc is None:
        raise TypeError("Argument slc may not be None")
      copyback_slc = False
      if slc is None:
        slc_ = None
        memview_slc = None
      else:
        try:
          memview_slc = memoryview(slc)
        except TypeError:
          try:
            _tmparray_slc = array.array("d",[0 for _ in range(len(slc))])
          except TypeError:
            raise TypeError("Argument slc has wrong type") from None
          else:
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
        else:
          if memview_slc.ndim != 1:
            raise TypeError("Argument slc must be one-dimensional")
          if memview_slc.format != "d":
            _tmparray_slc = array.array("d",slc)
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
      _res_getslc,_retargs_getslc = self.__obj.getslc_iO_3(whichsol,memview_slc)
      if _res_getslc != 0:
        _,_msg_getslc = self.__getlasterror(_res_getslc)
        raise Error(rescode(_res_getslc),_msg_getslc)
      if copyback_slc:
        for __tmp_524 in range(len(slc)): slc[__tmp_524] = slc_[__tmp_524]
    def __getslc_iO_2(self,whichsol):
      slc_ = bytearray(0)
      _res_getslc,_retargs_getslc = self.__obj.getslc_iO_2(whichsol,slc_)
      if _res_getslc != 0:
        _,_msg_getslc = self.__getlasterror(_res_getslc)
        raise Error(rescode(_res_getslc),_msg_getslc)
      slc = array.array("d")
      slc.frombytes(slc_)
      return (slc)
    def getslc(self,*args,**kwds):
      """
      Obtains the slc vector for a solution.
    
      getslc(whichsol,slc)
      getslc(whichsol) -> (slc)
        [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getslc_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getslc_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getaccdoty_iLO_4(self,whichsol,accidx,doty):
      if doty is None:
        raise TypeError("Argument doty may not be None")
      copyback_doty = False
      if doty is None:
        doty_ = None
        memview_doty = None
      else:
        try:
          memview_doty = memoryview(doty)
        except TypeError:
          try:
            _tmparray_doty = array.array("d",[0 for _ in range(len(doty))])
          except TypeError:
            raise TypeError("Argument doty has wrong type") from None
          else:
            memview_doty = memoryview(_tmparray_doty)
            copyback_doty = True
            doty_ = _tmparray_doty
        else:
          if memview_doty.ndim != 1:
            raise TypeError("Argument doty must be one-dimensional")
          if memview_doty.format != "d":
            _tmparray_doty = array.array("d",doty)
            memview_doty = memoryview(_tmparray_doty)
            copyback_doty = True
            doty_ = _tmparray_doty
      _res_getaccdoty,_retargs_getaccdoty = self.__obj.getaccdoty_iLO_4(whichsol,accidx,memview_doty)
      if _res_getaccdoty != 0:
        _,_msg_getaccdoty = self.__getlasterror(_res_getaccdoty)
        raise Error(rescode(_res_getaccdoty),_msg_getaccdoty)
      if copyback_doty:
        for __tmp_530 in range(len(doty)): doty[__tmp_530] = doty_[__tmp_530]
    def __getaccdoty_iLO_3(self,whichsol,accidx):
      doty_ = bytearray(0)
      _res_getaccdoty,_retargs_getaccdoty = self.__obj.getaccdoty_iLO_3(whichsol,accidx,doty_)
      if _res_getaccdoty != 0:
        _,_msg_getaccdoty = self.__getlasterror(_res_getaccdoty)
        raise Error(rescode(_res_getaccdoty),_msg_getaccdoty)
      doty = array.array("d")
      doty.frombytes(doty_)
      return (doty)
    def getaccdoty(self,*args,**kwds):
      """
      Obtains the doty vector for an affine conic constraint.
    
      getaccdoty(whichsol,accidx,doty)
      getaccdoty(whichsol,accidx) -> (doty)
        [accidx : int64]  The index of the affine conic constraint.  
        [doty : array(float64)]  The dual values for this affine conic constraint. The array should have length equal to the dimension of the constraint.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getaccdoty_iLO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getaccdoty_iLO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getaccdotys_iO_3(self,whichsol,doty):
      if doty is None:
        raise TypeError("Argument doty may not be None")
      copyback_doty = False
      if doty is None:
        doty_ = None
        memview_doty = None
      else:
        try:
          memview_doty = memoryview(doty)
        except TypeError:
          try:
            _tmparray_doty = array.array("d",[0 for _ in range(len(doty))])
          except TypeError:
            raise TypeError("Argument doty has wrong type") from None
          else:
            memview_doty = memoryview(_tmparray_doty)
            copyback_doty = True
            doty_ = _tmparray_doty
        else:
          if memview_doty.ndim != 1:
            raise TypeError("Argument doty must be one-dimensional")
          if memview_doty.format != "d":
            _tmparray_doty = array.array("d",doty)
            memview_doty = memoryview(_tmparray_doty)
            copyback_doty = True
            doty_ = _tmparray_doty
      _res_getaccdotys,_retargs_getaccdotys = self.__obj.getaccdotys_iO_3(whichsol,memview_doty)
      if _res_getaccdotys != 0:
        _,_msg_getaccdotys = self.__getlasterror(_res_getaccdotys)
        raise Error(rescode(_res_getaccdotys),_msg_getaccdotys)
      if copyback_doty:
        for __tmp_536 in range(len(doty)): doty[__tmp_536] = doty_[__tmp_536]
    def __getaccdotys_iO_2(self,whichsol):
      doty_ = bytearray(0)
      _res_getaccdotys,_retargs_getaccdotys = self.__obj.getaccdotys_iO_2(whichsol,doty_)
      if _res_getaccdotys != 0:
        _,_msg_getaccdotys = self.__getlasterror(_res_getaccdotys)
        raise Error(rescode(_res_getaccdotys),_msg_getaccdotys)
      doty = array.array("d")
      doty.frombytes(doty_)
      return (doty)
    def getaccdotys(self,*args,**kwds):
      """
      Obtains the doty vector for a solution.
    
      getaccdotys(whichsol,doty)
      getaccdotys(whichsol) -> (doty)
        [doty : array(float64)]  The dual values of affine conic constraints. The array should have length equal to the sum of dimensions of all affine conic constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getaccdotys_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getaccdotys_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __evaluateacc_iLO_4(self,whichsol,accidx,activity):
      if activity is None:
        raise TypeError("Argument activity may not be None")
      copyback_activity = False
      if activity is None:
        activity_ = None
        memview_activity = None
      else:
        try:
          memview_activity = memoryview(activity)
        except TypeError:
          try:
            _tmparray_activity = array.array("d",[0 for _ in range(len(activity))])
          except TypeError:
            raise TypeError("Argument activity has wrong type") from None
          else:
            memview_activity = memoryview(_tmparray_activity)
            copyback_activity = True
            activity_ = _tmparray_activity
        else:
          if memview_activity.ndim != 1:
            raise TypeError("Argument activity must be one-dimensional")
          if memview_activity.format != "d":
            _tmparray_activity = array.array("d",activity)
            memview_activity = memoryview(_tmparray_activity)
            copyback_activity = True
            activity_ = _tmparray_activity
      _res_evaluateacc,_retargs_evaluateacc = self.__obj.evaluateacc_iLO_4(whichsol,accidx,memview_activity)
      if _res_evaluateacc != 0:
        _,_msg_evaluateacc = self.__getlasterror(_res_evaluateacc)
        raise Error(rescode(_res_evaluateacc),_msg_evaluateacc)
      if copyback_activity:
        for __tmp_542 in range(len(activity)): activity[__tmp_542] = activity_[__tmp_542]
    def __evaluateacc_iLO_3(self,whichsol,accidx):
      activity_ = bytearray(0)
      _res_evaluateacc,_retargs_evaluateacc = self.__obj.evaluateacc_iLO_3(whichsol,accidx,activity_)
      if _res_evaluateacc != 0:
        _,_msg_evaluateacc = self.__getlasterror(_res_evaluateacc)
        raise Error(rescode(_res_evaluateacc),_msg_evaluateacc)
      activity = array.array("d")
      activity.frombytes(activity_)
      return (activity)
    def evaluateacc(self,*args,**kwds):
      """
      Evaluates the activity of an affine conic constraint.
    
      evaluateacc(whichsol,accidx,activity)
      evaluateacc(whichsol,accidx) -> (activity)
        [accidx : int64]  The index of the affine conic constraint.  
        [activity : array(float64)]  The activity of the affine conic constraint. The array should have length equal to the dimension of the constraint.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__evaluateacc_iLO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__evaluateacc_iLO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __evaluateaccs_iO_3(self,whichsol,activity):
      if activity is None:
        raise TypeError("Argument activity may not be None")
      copyback_activity = False
      if activity is None:
        activity_ = None
        memview_activity = None
      else:
        try:
          memview_activity = memoryview(activity)
        except TypeError:
          try:
            _tmparray_activity = array.array("d",[0 for _ in range(len(activity))])
          except TypeError:
            raise TypeError("Argument activity has wrong type") from None
          else:
            memview_activity = memoryview(_tmparray_activity)
            copyback_activity = True
            activity_ = _tmparray_activity
        else:
          if memview_activity.ndim != 1:
            raise TypeError("Argument activity must be one-dimensional")
          if memview_activity.format != "d":
            _tmparray_activity = array.array("d",activity)
            memview_activity = memoryview(_tmparray_activity)
            copyback_activity = True
            activity_ = _tmparray_activity
      _res_evaluateaccs,_retargs_evaluateaccs = self.__obj.evaluateaccs_iO_3(whichsol,memview_activity)
      if _res_evaluateaccs != 0:
        _,_msg_evaluateaccs = self.__getlasterror(_res_evaluateaccs)
        raise Error(rescode(_res_evaluateaccs),_msg_evaluateaccs)
      if copyback_activity:
        for __tmp_548 in range(len(activity)): activity[__tmp_548] = activity_[__tmp_548]
    def __evaluateaccs_iO_2(self,whichsol):
      activity_ = bytearray(0)
      _res_evaluateaccs,_retargs_evaluateaccs = self.__obj.evaluateaccs_iO_2(whichsol,activity_)
      if _res_evaluateaccs != 0:
        _,_msg_evaluateaccs = self.__getlasterror(_res_evaluateaccs)
        raise Error(rescode(_res_evaluateaccs),_msg_evaluateaccs)
      activity = array.array("d")
      activity.frombytes(activity_)
      return (activity)
    def evaluateaccs(self,*args,**kwds):
      """
      Evaluates the activities of all affine conic constraints.
    
      evaluateaccs(whichsol,activity)
      evaluateaccs(whichsol) -> (activity)
        [activity : array(float64)]  The activity of affine conic constraints. The array should have length equal to the sum of dimensions of all affine conic constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__evaluateaccs_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__evaluateaccs_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getsuc_iO_3(self,whichsol,suc):
      if suc is None:
        raise TypeError("Argument suc may not be None")
      copyback_suc = False
      if suc is None:
        suc_ = None
        memview_suc = None
      else:
        try:
          memview_suc = memoryview(suc)
        except TypeError:
          try:
            _tmparray_suc = array.array("d",[0 for _ in range(len(suc))])
          except TypeError:
            raise TypeError("Argument suc has wrong type") from None
          else:
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
        else:
          if memview_suc.ndim != 1:
            raise TypeError("Argument suc must be one-dimensional")
          if memview_suc.format != "d":
            _tmparray_suc = array.array("d",suc)
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
      _res_getsuc,_retargs_getsuc = self.__obj.getsuc_iO_3(whichsol,memview_suc)
      if _res_getsuc != 0:
        _,_msg_getsuc = self.__getlasterror(_res_getsuc)
        raise Error(rescode(_res_getsuc),_msg_getsuc)
      if copyback_suc:
        for __tmp_554 in range(len(suc)): suc[__tmp_554] = suc_[__tmp_554]
    def __getsuc_iO_2(self,whichsol):
      suc_ = bytearray(0)
      _res_getsuc,_retargs_getsuc = self.__obj.getsuc_iO_2(whichsol,suc_)
      if _res_getsuc != 0:
        _,_msg_getsuc = self.__getlasterror(_res_getsuc)
        raise Error(rescode(_res_getsuc),_msg_getsuc)
      suc = array.array("d")
      suc.frombytes(suc_)
      return (suc)
    def getsuc(self,*args,**kwds):
      """
      Obtains the suc vector for a solution.
    
      getsuc(whichsol,suc)
      getsuc(whichsol) -> (suc)
        [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getsuc_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getsuc_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getslx_iO_3(self,whichsol,slx):
      if slx is None:
        raise TypeError("Argument slx may not be None")
      copyback_slx = False
      if slx is None:
        slx_ = None
        memview_slx = None
      else:
        try:
          memview_slx = memoryview(slx)
        except TypeError:
          try:
            _tmparray_slx = array.array("d",[0 for _ in range(len(slx))])
          except TypeError:
            raise TypeError("Argument slx has wrong type") from None
          else:
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
        else:
          if memview_slx.ndim != 1:
            raise TypeError("Argument slx must be one-dimensional")
          if memview_slx.format != "d":
            _tmparray_slx = array.array("d",slx)
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
      _res_getslx,_retargs_getslx = self.__obj.getslx_iO_3(whichsol,memview_slx)
      if _res_getslx != 0:
        _,_msg_getslx = self.__getlasterror(_res_getslx)
        raise Error(rescode(_res_getslx),_msg_getslx)
      if copyback_slx:
        for __tmp_560 in range(len(slx)): slx[__tmp_560] = slx_[__tmp_560]
    def __getslx_iO_2(self,whichsol):
      slx_ = bytearray(0)
      _res_getslx,_retargs_getslx = self.__obj.getslx_iO_2(whichsol,slx_)
      if _res_getslx != 0:
        _,_msg_getslx = self.__getlasterror(_res_getslx)
        raise Error(rescode(_res_getslx),_msg_getslx)
      slx = array.array("d")
      slx.frombytes(slx_)
      return (slx)
    def getslx(self,*args,**kwds):
      """
      Obtains the slx vector for a solution.
    
      getslx(whichsol,slx)
      getslx(whichsol) -> (slx)
        [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getslx_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getslx_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getsux_iO_3(self,whichsol,sux):
      if sux is None:
        raise TypeError("Argument sux may not be None")
      copyback_sux = False
      if sux is None:
        sux_ = None
        memview_sux = None
      else:
        try:
          memview_sux = memoryview(sux)
        except TypeError:
          try:
            _tmparray_sux = array.array("d",[0 for _ in range(len(sux))])
          except TypeError:
            raise TypeError("Argument sux has wrong type") from None
          else:
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
        else:
          if memview_sux.ndim != 1:
            raise TypeError("Argument sux must be one-dimensional")
          if memview_sux.format != "d":
            _tmparray_sux = array.array("d",sux)
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
      _res_getsux,_retargs_getsux = self.__obj.getsux_iO_3(whichsol,memview_sux)
      if _res_getsux != 0:
        _,_msg_getsux = self.__getlasterror(_res_getsux)
        raise Error(rescode(_res_getsux),_msg_getsux)
      if copyback_sux:
        for __tmp_566 in range(len(sux)): sux[__tmp_566] = sux_[__tmp_566]
    def __getsux_iO_2(self,whichsol):
      sux_ = bytearray(0)
      _res_getsux,_retargs_getsux = self.__obj.getsux_iO_2(whichsol,sux_)
      if _res_getsux != 0:
        _,_msg_getsux = self.__getlasterror(_res_getsux)
        raise Error(rescode(_res_getsux),_msg_getsux)
      sux = array.array("d")
      sux.frombytes(sux_)
      return (sux)
    def getsux(self,*args,**kwds):
      """
      Obtains the sux vector for a solution.
    
      getsux(whichsol,sux)
      getsux(whichsol) -> (sux)
        [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getsux_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getsux_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getsnx_iO_3(self,whichsol,snx):
      if snx is None:
        raise TypeError("Argument snx may not be None")
      copyback_snx = False
      if snx is None:
        snx_ = None
        memview_snx = None
      else:
        try:
          memview_snx = memoryview(snx)
        except TypeError:
          try:
            _tmparray_snx = array.array("d",[0 for _ in range(len(snx))])
          except TypeError:
            raise TypeError("Argument snx has wrong type") from None
          else:
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
        else:
          if memview_snx.ndim != 1:
            raise TypeError("Argument snx must be one-dimensional")
          if memview_snx.format != "d":
            _tmparray_snx = array.array("d",snx)
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
      _res_getsnx,_retargs_getsnx = self.__obj.getsnx_iO_3(whichsol,memview_snx)
      if _res_getsnx != 0:
        _,_msg_getsnx = self.__getlasterror(_res_getsnx)
        raise Error(rescode(_res_getsnx),_msg_getsnx)
      if copyback_snx:
        for __tmp_572 in range(len(snx)): snx[__tmp_572] = snx_[__tmp_572]
    def __getsnx_iO_2(self,whichsol):
      snx_ = bytearray(0)
      _res_getsnx,_retargs_getsnx = self.__obj.getsnx_iO_2(whichsol,snx_)
      if _res_getsnx != 0:
        _,_msg_getsnx = self.__getlasterror(_res_getsnx)
        raise Error(rescode(_res_getsnx),_msg_getsnx)
      snx = array.array("d")
      snx.frombytes(snx_)
      return (snx)
    def getsnx(self,*args,**kwds):
      """
      Obtains the snx vector for a solution.
    
      getsnx(whichsol,snx)
      getsnx(whichsol) -> (snx)
        [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getsnx_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getsnx_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getskcslice_iiiO_5(self,whichsol,first,last,skc):
      if skc is None:
        skc_ = None
      else:
        # o
        _tmparray_skc_ = array.array("i",[0 for _ in range(len(skc))])
        skc_ = memoryview(_tmparray_skc_)
      _res_getskcslice,_retargs_getskcslice = self.__obj.getskcslice_iiiO_5(whichsol,first,last,skc_)
      if _res_getskcslice != 0:
        _,_msg_getskcslice = self.__getlasterror(_res_getskcslice)
        raise Error(rescode(_res_getskcslice),_msg_getskcslice)
      for __tmp_576 in range(len(skc)): skc[__tmp_576] = stakey(skc_[__tmp_576])
    def __getskcslice_iiiO_4(self,whichsol,first,last):
      skc_ = bytearray(0)
      _res_getskcslice,_retargs_getskcslice = self.__obj.getskcslice_iiiO_4(whichsol,first,last,skc_)
      if _res_getskcslice != 0:
        _,_msg_getskcslice = self.__getlasterror(_res_getskcslice)
        raise Error(rescode(_res_getskcslice),_msg_getskcslice)
      skc_ints = array.array("i")
      skc_ints.frombytes(skc_)
      skc = [ stakey(__tmp_577) for __tmp_577 in skc_ints ]
      return (skc)
    def getskcslice(self,*args,**kwds):
      """
      Obtains the status keys for a slice of the constraints.
    
      getskcslice(whichsol,first,last,skc)
      getskcslice(whichsol,first,last) -> (skc)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [skc : array(mosek.stakey)]  Status keys for the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getskcslice_iiiO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__getskcslice_iiiO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getskxslice_iiiO_5(self,whichsol,first,last,skx):
      if skx is None:
        skx_ = None
      else:
        # o
        _tmparray_skx_ = array.array("i",[0 for _ in range(len(skx))])
        skx_ = memoryview(_tmparray_skx_)
      _res_getskxslice,_retargs_getskxslice = self.__obj.getskxslice_iiiO_5(whichsol,first,last,skx_)
      if _res_getskxslice != 0:
        _,_msg_getskxslice = self.__getlasterror(_res_getskxslice)
        raise Error(rescode(_res_getskxslice),_msg_getskxslice)
      for __tmp_578 in range(len(skx)): skx[__tmp_578] = stakey(skx_[__tmp_578])
    def __getskxslice_iiiO_4(self,whichsol,first,last):
      skx_ = bytearray(0)
      _res_getskxslice,_retargs_getskxslice = self.__obj.getskxslice_iiiO_4(whichsol,first,last,skx_)
      if _res_getskxslice != 0:
        _,_msg_getskxslice = self.__getlasterror(_res_getskxslice)
        raise Error(rescode(_res_getskxslice),_msg_getskxslice)
      skx_ints = array.array("i")
      skx_ints.frombytes(skx_)
      skx = [ stakey(__tmp_579) for __tmp_579 in skx_ints ]
      return (skx)
    def getskxslice(self,*args,**kwds):
      """
      Obtains the status keys for a slice of the scalar variables.
    
      getskxslice(whichsol,first,last,skx)
      getskxslice(whichsol,first,last) -> (skx)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [skx : array(mosek.stakey)]  Status keys for the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getskxslice_iiiO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__getskxslice_iiiO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getxcslice_iiiO_5(self,whichsol,first,last,xc):
      copyback_xc = False
      if xc is None:
        xc_ = None
        memview_xc = None
      else:
        try:
          memview_xc = memoryview(xc)
        except TypeError:
          try:
            _tmparray_xc = array.array("d",[0 for _ in range(len(xc))])
          except TypeError:
            raise TypeError("Argument xc has wrong type") from None
          else:
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
        else:
          if memview_xc.ndim != 1:
            raise TypeError("Argument xc must be one-dimensional")
          if memview_xc.format != "d":
            _tmparray_xc = array.array("d",xc)
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
      _res_getxcslice,_retargs_getxcslice = self.__obj.getxcslice_iiiO_5(whichsol,first,last,memview_xc)
      if _res_getxcslice != 0:
        _,_msg_getxcslice = self.__getlasterror(_res_getxcslice)
        raise Error(rescode(_res_getxcslice),_msg_getxcslice)
      if copyback_xc:
        for __tmp_580 in range(len(xc)): xc[__tmp_580] = xc_[__tmp_580]
    def __getxcslice_iiiO_4(self,whichsol,first,last):
      xc_ = bytearray(0)
      _res_getxcslice,_retargs_getxcslice = self.__obj.getxcslice_iiiO_4(whichsol,first,last,xc_)
      if _res_getxcslice != 0:
        _,_msg_getxcslice = self.__getlasterror(_res_getxcslice)
        raise Error(rescode(_res_getxcslice),_msg_getxcslice)
      xc = array.array("d")
      xc.frombytes(xc_)
      return (xc)
    def getxcslice(self,*args,**kwds):
      """
      Obtains a slice of the xc vector for a solution.
    
      getxcslice(whichsol,first,last,xc)
      getxcslice(whichsol,first,last) -> (xc)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [xc : array(float64)]  Primal constraint solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getxcslice_iiiO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__getxcslice_iiiO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getxxslice_iiiO_5(self,whichsol,first,last,xx):
      copyback_xx = False
      if xx is None:
        xx_ = None
        memview_xx = None
      else:
        try:
          memview_xx = memoryview(xx)
        except TypeError:
          try:
            _tmparray_xx = array.array("d",[0 for _ in range(len(xx))])
          except TypeError:
            raise TypeError("Argument xx has wrong type") from None
          else:
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
        else:
          if memview_xx.ndim != 1:
            raise TypeError("Argument xx must be one-dimensional")
          if memview_xx.format != "d":
            _tmparray_xx = array.array("d",xx)
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
      _res_getxxslice,_retargs_getxxslice = self.__obj.getxxslice_iiiO_5(whichsol,first,last,memview_xx)
      if _res_getxxslice != 0:
        _,_msg_getxxslice = self.__getlasterror(_res_getxxslice)
        raise Error(rescode(_res_getxxslice),_msg_getxxslice)
      if copyback_xx:
        for __tmp_582 in range(len(xx)): xx[__tmp_582] = xx_[__tmp_582]
    def __getxxslice_iiiO_4(self,whichsol,first,last):
      xx_ = bytearray(0)
      _res_getxxslice,_retargs_getxxslice = self.__obj.getxxslice_iiiO_4(whichsol,first,last,xx_)
      if _res_getxxslice != 0:
        _,_msg_getxxslice = self.__getlasterror(_res_getxxslice)
        raise Error(rescode(_res_getxxslice),_msg_getxxslice)
      xx = array.array("d")
      xx.frombytes(xx_)
      return (xx)
    def getxxslice(self,*args,**kwds):
      """
      Obtains a slice of the xx vector for a solution.
    
      getxxslice(whichsol,first,last,xx)
      getxxslice(whichsol,first,last) -> (xx)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [xx : array(float64)]  Primal variable solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getxxslice_iiiO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__getxxslice_iiiO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getyslice_iiiO_5(self,whichsol,first,last,y):
      copyback_y = False
      if y is None:
        y_ = None
        memview_y = None
      else:
        try:
          memview_y = memoryview(y)
        except TypeError:
          try:
            _tmparray_y = array.array("d",[0 for _ in range(len(y))])
          except TypeError:
            raise TypeError("Argument y has wrong type") from None
          else:
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
        else:
          if memview_y.ndim != 1:
            raise TypeError("Argument y must be one-dimensional")
          if memview_y.format != "d":
            _tmparray_y = array.array("d",y)
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
      _res_getyslice,_retargs_getyslice = self.__obj.getyslice_iiiO_5(whichsol,first,last,memview_y)
      if _res_getyslice != 0:
        _,_msg_getyslice = self.__getlasterror(_res_getyslice)
        raise Error(rescode(_res_getyslice),_msg_getyslice)
      if copyback_y:
        for __tmp_584 in range(len(y)): y[__tmp_584] = y_[__tmp_584]
    def __getyslice_iiiO_4(self,whichsol,first,last):
      y_ = bytearray(0)
      _res_getyslice,_retargs_getyslice = self.__obj.getyslice_iiiO_4(whichsol,first,last,y_)
      if _res_getyslice != 0:
        _,_msg_getyslice = self.__getlasterror(_res_getyslice)
        raise Error(rescode(_res_getyslice),_msg_getyslice)
      y = array.array("d")
      y.frombytes(y_)
      return (y)
    def getyslice(self,*args,**kwds):
      """
      Obtains a slice of the y vector for a solution.
    
      getyslice(whichsol,first,last,y)
      getyslice(whichsol,first,last) -> (y)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getyslice_iiiO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__getyslice_iiiO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getslcslice_iiiO_5(self,whichsol,first,last,slc):
      copyback_slc = False
      if slc is None:
        slc_ = None
        memview_slc = None
      else:
        try:
          memview_slc = memoryview(slc)
        except TypeError:
          try:
            _tmparray_slc = array.array("d",[0 for _ in range(len(slc))])
          except TypeError:
            raise TypeError("Argument slc has wrong type") from None
          else:
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
        else:
          if memview_slc.ndim != 1:
            raise TypeError("Argument slc must be one-dimensional")
          if memview_slc.format != "d":
            _tmparray_slc = array.array("d",slc)
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
      _res_getslcslice,_retargs_getslcslice = self.__obj.getslcslice_iiiO_5(whichsol,first,last,memview_slc)
      if _res_getslcslice != 0:
        _,_msg_getslcslice = self.__getlasterror(_res_getslcslice)
        raise Error(rescode(_res_getslcslice),_msg_getslcslice)
      if copyback_slc:
        for __tmp_586 in range(len(slc)): slc[__tmp_586] = slc_[__tmp_586]
    def __getslcslice_iiiO_4(self,whichsol,first,last):
      slc_ = bytearray(0)
      _res_getslcslice,_retargs_getslcslice = self.__obj.getslcslice_iiiO_4(whichsol,first,last,slc_)
      if _res_getslcslice != 0:
        _,_msg_getslcslice = self.__getlasterror(_res_getslcslice)
        raise Error(rescode(_res_getslcslice),_msg_getslcslice)
      slc = array.array("d")
      slc.frombytes(slc_)
      return (slc)
    def getslcslice(self,*args,**kwds):
      """
      Obtains a slice of the slc vector for a solution.
    
      getslcslice(whichsol,first,last,slc)
      getslcslice(whichsol,first,last) -> (slc)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getslcslice_iiiO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__getslcslice_iiiO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getsucslice_iiiO_5(self,whichsol,first,last,suc):
      copyback_suc = False
      if suc is None:
        suc_ = None
        memview_suc = None
      else:
        try:
          memview_suc = memoryview(suc)
        except TypeError:
          try:
            _tmparray_suc = array.array("d",[0 for _ in range(len(suc))])
          except TypeError:
            raise TypeError("Argument suc has wrong type") from None
          else:
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
        else:
          if memview_suc.ndim != 1:
            raise TypeError("Argument suc must be one-dimensional")
          if memview_suc.format != "d":
            _tmparray_suc = array.array("d",suc)
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
      _res_getsucslice,_retargs_getsucslice = self.__obj.getsucslice_iiiO_5(whichsol,first,last,memview_suc)
      if _res_getsucslice != 0:
        _,_msg_getsucslice = self.__getlasterror(_res_getsucslice)
        raise Error(rescode(_res_getsucslice),_msg_getsucslice)
      if copyback_suc:
        for __tmp_588 in range(len(suc)): suc[__tmp_588] = suc_[__tmp_588]
    def __getsucslice_iiiO_4(self,whichsol,first,last):
      suc_ = bytearray(0)
      _res_getsucslice,_retargs_getsucslice = self.__obj.getsucslice_iiiO_4(whichsol,first,last,suc_)
      if _res_getsucslice != 0:
        _,_msg_getsucslice = self.__getlasterror(_res_getsucslice)
        raise Error(rescode(_res_getsucslice),_msg_getsucslice)
      suc = array.array("d")
      suc.frombytes(suc_)
      return (suc)
    def getsucslice(self,*args,**kwds):
      """
      Obtains a slice of the suc vector for a solution.
    
      getsucslice(whichsol,first,last,suc)
      getsucslice(whichsol,first,last) -> (suc)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getsucslice_iiiO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__getsucslice_iiiO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getslxslice_iiiO_5(self,whichsol,first,last,slx):
      copyback_slx = False
      if slx is None:
        slx_ = None
        memview_slx = None
      else:
        try:
          memview_slx = memoryview(slx)
        except TypeError:
          try:
            _tmparray_slx = array.array("d",[0 for _ in range(len(slx))])
          except TypeError:
            raise TypeError("Argument slx has wrong type") from None
          else:
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
        else:
          if memview_slx.ndim != 1:
            raise TypeError("Argument slx must be one-dimensional")
          if memview_slx.format != "d":
            _tmparray_slx = array.array("d",slx)
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
      _res_getslxslice,_retargs_getslxslice = self.__obj.getslxslice_iiiO_5(whichsol,first,last,memview_slx)
      if _res_getslxslice != 0:
        _,_msg_getslxslice = self.__getlasterror(_res_getslxslice)
        raise Error(rescode(_res_getslxslice),_msg_getslxslice)
      if copyback_slx:
        for __tmp_590 in range(len(slx)): slx[__tmp_590] = slx_[__tmp_590]
    def __getslxslice_iiiO_4(self,whichsol,first,last):
      slx_ = bytearray(0)
      _res_getslxslice,_retargs_getslxslice = self.__obj.getslxslice_iiiO_4(whichsol,first,last,slx_)
      if _res_getslxslice != 0:
        _,_msg_getslxslice = self.__getlasterror(_res_getslxslice)
        raise Error(rescode(_res_getslxslice),_msg_getslxslice)
      slx = array.array("d")
      slx.frombytes(slx_)
      return (slx)
    def getslxslice(self,*args,**kwds):
      """
      Obtains a slice of the slx vector for a solution.
    
      getslxslice(whichsol,first,last,slx)
      getslxslice(whichsol,first,last) -> (slx)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getslxslice_iiiO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__getslxslice_iiiO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getsuxslice_iiiO_5(self,whichsol,first,last,sux):
      copyback_sux = False
      if sux is None:
        sux_ = None
        memview_sux = None
      else:
        try:
          memview_sux = memoryview(sux)
        except TypeError:
          try:
            _tmparray_sux = array.array("d",[0 for _ in range(len(sux))])
          except TypeError:
            raise TypeError("Argument sux has wrong type") from None
          else:
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
        else:
          if memview_sux.ndim != 1:
            raise TypeError("Argument sux must be one-dimensional")
          if memview_sux.format != "d":
            _tmparray_sux = array.array("d",sux)
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
      _res_getsuxslice,_retargs_getsuxslice = self.__obj.getsuxslice_iiiO_5(whichsol,first,last,memview_sux)
      if _res_getsuxslice != 0:
        _,_msg_getsuxslice = self.__getlasterror(_res_getsuxslice)
        raise Error(rescode(_res_getsuxslice),_msg_getsuxslice)
      if copyback_sux:
        for __tmp_592 in range(len(sux)): sux[__tmp_592] = sux_[__tmp_592]
    def __getsuxslice_iiiO_4(self,whichsol,first,last):
      sux_ = bytearray(0)
      _res_getsuxslice,_retargs_getsuxslice = self.__obj.getsuxslice_iiiO_4(whichsol,first,last,sux_)
      if _res_getsuxslice != 0:
        _,_msg_getsuxslice = self.__getlasterror(_res_getsuxslice)
        raise Error(rescode(_res_getsuxslice),_msg_getsuxslice)
      sux = array.array("d")
      sux.frombytes(sux_)
      return (sux)
    def getsuxslice(self,*args,**kwds):
      """
      Obtains a slice of the sux vector for a solution.
    
      getsuxslice(whichsol,first,last,sux)
      getsuxslice(whichsol,first,last) -> (sux)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getsuxslice_iiiO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__getsuxslice_iiiO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getsnxslice_iiiO_5(self,whichsol,first,last,snx):
      copyback_snx = False
      if snx is None:
        snx_ = None
        memview_snx = None
      else:
        try:
          memview_snx = memoryview(snx)
        except TypeError:
          try:
            _tmparray_snx = array.array("d",[0 for _ in range(len(snx))])
          except TypeError:
            raise TypeError("Argument snx has wrong type") from None
          else:
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
        else:
          if memview_snx.ndim != 1:
            raise TypeError("Argument snx must be one-dimensional")
          if memview_snx.format != "d":
            _tmparray_snx = array.array("d",snx)
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
      _res_getsnxslice,_retargs_getsnxslice = self.__obj.getsnxslice_iiiO_5(whichsol,first,last,memview_snx)
      if _res_getsnxslice != 0:
        _,_msg_getsnxslice = self.__getlasterror(_res_getsnxslice)
        raise Error(rescode(_res_getsnxslice),_msg_getsnxslice)
      if copyback_snx:
        for __tmp_594 in range(len(snx)): snx[__tmp_594] = snx_[__tmp_594]
    def __getsnxslice_iiiO_4(self,whichsol,first,last):
      snx_ = bytearray(0)
      _res_getsnxslice,_retargs_getsnxslice = self.__obj.getsnxslice_iiiO_4(whichsol,first,last,snx_)
      if _res_getsnxslice != 0:
        _,_msg_getsnxslice = self.__getlasterror(_res_getsnxslice)
        raise Error(rescode(_res_getsnxslice),_msg_getsnxslice)
      snx = array.array("d")
      snx.frombytes(snx_)
      return (snx)
    def getsnxslice(self,*args,**kwds):
      """
      Obtains a slice of the snx vector for a solution.
    
      getsnxslice(whichsol,first,last,snx)
      getsnxslice(whichsol,first,last) -> (snx)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getsnxslice_iiiO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__getsnxslice_iiiO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getbarxj_iiO_4(self,whichsol,j,barxj):
      if barxj is None:
        raise TypeError("Argument barxj may not be None")
      copyback_barxj = False
      if barxj is None:
        barxj_ = None
        memview_barxj = None
      else:
        try:
          memview_barxj = memoryview(barxj)
        except TypeError:
          try:
            _tmparray_barxj = array.array("d",[0 for _ in range(len(barxj))])
          except TypeError:
            raise TypeError("Argument barxj has wrong type") from None
          else:
            memview_barxj = memoryview(_tmparray_barxj)
            copyback_barxj = True
            barxj_ = _tmparray_barxj
        else:
          if memview_barxj.ndim != 1:
            raise TypeError("Argument barxj must be one-dimensional")
          if memview_barxj.format != "d":
            _tmparray_barxj = array.array("d",barxj)
            memview_barxj = memoryview(_tmparray_barxj)
            copyback_barxj = True
            barxj_ = _tmparray_barxj
      _res_getbarxj,_retargs_getbarxj = self.__obj.getbarxj_iiO_4(whichsol,j,memview_barxj)
      if _res_getbarxj != 0:
        _,_msg_getbarxj = self.__getlasterror(_res_getbarxj)
        raise Error(rescode(_res_getbarxj),_msg_getbarxj)
      if copyback_barxj:
        for __tmp_598 in range(len(barxj)): barxj[__tmp_598] = barxj_[__tmp_598]
    def __getbarxj_iiO_3(self,whichsol,j):
      barxj_ = bytearray(0)
      _res_getbarxj,_retargs_getbarxj = self.__obj.getbarxj_iiO_3(whichsol,j,barxj_)
      if _res_getbarxj != 0:
        _,_msg_getbarxj = self.__getlasterror(_res_getbarxj)
        raise Error(rescode(_res_getbarxj),_msg_getbarxj)
      barxj = array.array("d")
      barxj.frombytes(barxj_)
      return (barxj)
    def getbarxj(self,*args,**kwds):
      """
      Obtains the primal solution for a semidefinite variable.
    
      getbarxj(whichsol,j,barxj)
      getbarxj(whichsol,j) -> (barxj)
        [barxj : array(float64)]  Value of the j'th variable of barx.  
        [j : int32]  Index of the semidefinite variable.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getbarxj_iiO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getbarxj_iiO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getbarxslice_iiiLO_6(self,whichsol,first,last,slicesize,barxslice):
      if barxslice is None:
        raise TypeError("Argument barxslice may not be None")
      copyback_barxslice = False
      if barxslice is None:
        barxslice_ = None
        memview_barxslice = None
      else:
        try:
          memview_barxslice = memoryview(barxslice)
        except TypeError:
          try:
            _tmparray_barxslice = array.array("d",[0 for _ in range(len(barxslice))])
          except TypeError:
            raise TypeError("Argument barxslice has wrong type") from None
          else:
            memview_barxslice = memoryview(_tmparray_barxslice)
            copyback_barxslice = True
            barxslice_ = _tmparray_barxslice
        else:
          if memview_barxslice.ndim != 1:
            raise TypeError("Argument barxslice must be one-dimensional")
          if memview_barxslice.format != "d":
            _tmparray_barxslice = array.array("d",barxslice)
            memview_barxslice = memoryview(_tmparray_barxslice)
            copyback_barxslice = True
            barxslice_ = _tmparray_barxslice
      _res_getbarxslice,_retargs_getbarxslice = self.__obj.getbarxslice_iiiLO_6(whichsol,first,last,slicesize,memview_barxslice)
      if _res_getbarxslice != 0:
        _,_msg_getbarxslice = self.__getlasterror(_res_getbarxslice)
        raise Error(rescode(_res_getbarxslice),_msg_getbarxslice)
      if copyback_barxslice:
        for __tmp_602 in range(len(barxslice)): barxslice[__tmp_602] = barxslice_[__tmp_602]
    def __getbarxslice_iiiLO_5(self,whichsol,first,last,slicesize):
      barxslice_ = bytearray(0)
      _res_getbarxslice,_retargs_getbarxslice = self.__obj.getbarxslice_iiiLO_5(whichsol,first,last,slicesize,barxslice_)
      if _res_getbarxslice != 0:
        _,_msg_getbarxslice = self.__getlasterror(_res_getbarxslice)
        raise Error(rescode(_res_getbarxslice),_msg_getbarxslice)
      barxslice = array.array("d")
      barxslice.frombytes(barxslice_)
      return (barxslice)
    def getbarxslice(self,*args,**kwds):
      """
      Obtains the primal solution for a sequence of semidefinite variables.
    
      getbarxslice(whichsol,first,last,slicesize,barxslice)
      getbarxslice(whichsol,first,last,slicesize) -> (barxslice)
        [barxslice : array(float64)]  Solution values of symmetric matrix variables in the slice, stored sequentially.  
        [first : int32]  Index of the first semidefinite variable in the slice.  
        [last : int32]  Index of the last semidefinite variable in the slice plus one.  
        [slicesize : int64]  Denotes the length of the array barxslice.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__getbarxslice_iiiLO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 5: return self.__getbarxslice_iiiLO_5(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getbarsj_iiO_4(self,whichsol,j,barsj):
      if barsj is None:
        raise TypeError("Argument barsj may not be None")
      copyback_barsj = False
      if barsj is None:
        barsj_ = None
        memview_barsj = None
      else:
        try:
          memview_barsj = memoryview(barsj)
        except TypeError:
          try:
            _tmparray_barsj = array.array("d",[0 for _ in range(len(barsj))])
          except TypeError:
            raise TypeError("Argument barsj has wrong type") from None
          else:
            memview_barsj = memoryview(_tmparray_barsj)
            copyback_barsj = True
            barsj_ = _tmparray_barsj
        else:
          if memview_barsj.ndim != 1:
            raise TypeError("Argument barsj must be one-dimensional")
          if memview_barsj.format != "d":
            _tmparray_barsj = array.array("d",barsj)
            memview_barsj = memoryview(_tmparray_barsj)
            copyback_barsj = True
            barsj_ = _tmparray_barsj
      _res_getbarsj,_retargs_getbarsj = self.__obj.getbarsj_iiO_4(whichsol,j,memview_barsj)
      if _res_getbarsj != 0:
        _,_msg_getbarsj = self.__getlasterror(_res_getbarsj)
        raise Error(rescode(_res_getbarsj),_msg_getbarsj)
      if copyback_barsj:
        for __tmp_606 in range(len(barsj)): barsj[__tmp_606] = barsj_[__tmp_606]
    def __getbarsj_iiO_3(self,whichsol,j):
      barsj_ = bytearray(0)
      _res_getbarsj,_retargs_getbarsj = self.__obj.getbarsj_iiO_3(whichsol,j,barsj_)
      if _res_getbarsj != 0:
        _,_msg_getbarsj = self.__getlasterror(_res_getbarsj)
        raise Error(rescode(_res_getbarsj),_msg_getbarsj)
      barsj = array.array("d")
      barsj.frombytes(barsj_)
      return (barsj)
    def getbarsj(self,*args,**kwds):
      """
      Obtains the dual solution for a semidefinite variable.
    
      getbarsj(whichsol,j,barsj)
      getbarsj(whichsol,j) -> (barsj)
        [barsj : array(float64)]  Value of the j'th dual variable of barx.  
        [j : int32]  Index of the semidefinite variable.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getbarsj_iiO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getbarsj_iiO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getbarsslice_iiiLO_6(self,whichsol,first,last,slicesize,barsslice):
      if barsslice is None:
        raise TypeError("Argument barsslice may not be None")
      copyback_barsslice = False
      if barsslice is None:
        barsslice_ = None
        memview_barsslice = None
      else:
        try:
          memview_barsslice = memoryview(barsslice)
        except TypeError:
          try:
            _tmparray_barsslice = array.array("d",[0 for _ in range(len(barsslice))])
          except TypeError:
            raise TypeError("Argument barsslice has wrong type") from None
          else:
            memview_barsslice = memoryview(_tmparray_barsslice)
            copyback_barsslice = True
            barsslice_ = _tmparray_barsslice
        else:
          if memview_barsslice.ndim != 1:
            raise TypeError("Argument barsslice must be one-dimensional")
          if memview_barsslice.format != "d":
            _tmparray_barsslice = array.array("d",barsslice)
            memview_barsslice = memoryview(_tmparray_barsslice)
            copyback_barsslice = True
            barsslice_ = _tmparray_barsslice
      _res_getbarsslice,_retargs_getbarsslice = self.__obj.getbarsslice_iiiLO_6(whichsol,first,last,slicesize,memview_barsslice)
      if _res_getbarsslice != 0:
        _,_msg_getbarsslice = self.__getlasterror(_res_getbarsslice)
        raise Error(rescode(_res_getbarsslice),_msg_getbarsslice)
      if copyback_barsslice:
        for __tmp_610 in range(len(barsslice)): barsslice[__tmp_610] = barsslice_[__tmp_610]
    def __getbarsslice_iiiLO_5(self,whichsol,first,last,slicesize):
      barsslice_ = bytearray(0)
      _res_getbarsslice,_retargs_getbarsslice = self.__obj.getbarsslice_iiiLO_5(whichsol,first,last,slicesize,barsslice_)
      if _res_getbarsslice != 0:
        _,_msg_getbarsslice = self.__getlasterror(_res_getbarsslice)
        raise Error(rescode(_res_getbarsslice),_msg_getbarsslice)
      barsslice = array.array("d")
      barsslice.frombytes(barsslice_)
      return (barsslice)
    def getbarsslice(self,*args,**kwds):
      """
      Obtains the dual solution for a sequence of semidefinite variables.
    
      getbarsslice(whichsol,first,last,slicesize,barsslice)
      getbarsslice(whichsol,first,last,slicesize) -> (barsslice)
        [barsslice : array(float64)]  Dual solution values of symmetric matrix variables in the slice, stored sequentially.  
        [first : int32]  Index of the first semidefinite variable in the slice.  
        [last : int32]  Index of the last semidefinite variable in the slice plus one.  
        [slicesize : int64]  Denotes the length of the array barsslice.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__getbarsslice_iiiLO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 5: return self.__getbarsslice_iiiLO_5(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __putskc_iO_3(self,whichsol,skc):
      if skc is None:
        skc_ = None
      else:
        # i
        _tmparray_skc_ = array.array("i",skc)
        skc_ = memoryview(_tmparray_skc_)
      _res_putskc,_retargs_putskc = self.__obj.putskc_iO_3(whichsol,skc_)
      if _res_putskc != 0:
        _,_msg_putskc = self.__getlasterror(_res_putskc)
        raise Error(rescode(_res_putskc),_msg_putskc)
    def putskc(self,*args,**kwds):
      """
      Sets the status keys for the constraints.
    
      putskc(whichsol,skc)
        [skc : array(mosek.stakey)]  Status keys for the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putskc_iO_3(*args,**kwds)
    def __putskx_iO_3(self,whichsol,skx):
      if skx is None:
        skx_ = None
      else:
        # i
        _tmparray_skx_ = array.array("i",skx)
        skx_ = memoryview(_tmparray_skx_)
      _res_putskx,_retargs_putskx = self.__obj.putskx_iO_3(whichsol,skx_)
      if _res_putskx != 0:
        _,_msg_putskx = self.__getlasterror(_res_putskx)
        raise Error(rescode(_res_putskx),_msg_putskx)
    def putskx(self,*args,**kwds):
      """
      Sets the status keys for the scalar variables.
    
      putskx(whichsol,skx)
        [skx : array(mosek.stakey)]  Status keys for the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putskx_iO_3(*args,**kwds)
    def __putxc_iO_3(self,whichsol,xc):
      if xc is None:
        raise TypeError("Argument xc may not be None")
      copyback_xc = False
      if xc is None:
        xc_ = None
        memview_xc = None
      else:
        try:
          memview_xc = memoryview(xc)
        except TypeError:
          try:
            _tmparray_xc = array.array("d",[0 for _ in range(len(xc))])
          except TypeError:
            raise TypeError("Argument xc has wrong type") from None
          else:
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
        else:
          if memview_xc.ndim != 1:
            raise TypeError("Argument xc must be one-dimensional")
          if memview_xc.format != "d":
            _tmparray_xc = array.array("d",xc)
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
      _res_putxc,_retargs_putxc = self.__obj.putxc_iO_3(whichsol,memview_xc)
      if _res_putxc != 0:
        _,_msg_putxc = self.__getlasterror(_res_putxc)
        raise Error(rescode(_res_putxc),_msg_putxc)
      if copyback_xc:
        for __tmp_626 in range(len(xc)): xc[__tmp_626] = xc_[__tmp_626]
    def __putxc_iO_2(self,whichsol):
      xc_ = bytearray(0)
      _res_putxc,_retargs_putxc = self.__obj.putxc_iO_2(whichsol,xc_)
      if _res_putxc != 0:
        _,_msg_putxc = self.__getlasterror(_res_putxc)
        raise Error(rescode(_res_putxc),_msg_putxc)
      xc = array.array("d")
      xc.frombytes(xc_)
      return (xc)
    def putxc(self,*args,**kwds):
      """
      Sets the xc vector for a solution.
    
      putxc(whichsol,xc)
      putxc(whichsol) -> (xc)
        [whichsol : mosek.soltype]  Selects a solution.  
        [xc : array(float64)]  Primal constraint solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__putxc_iO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__putxc_iO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __putxx_iO_3(self,whichsol,xx):
      if xx is None:
        raise TypeError("Argument xx may not be None")
      copyback_xx = False
      if xx is None:
        xx_ = None
        memview_xx = None
      else:
        try:
          memview_xx = memoryview(xx)
        except TypeError:
          try:
            _tmparray_xx = array.array("d",xx)
          except TypeError:
            raise TypeError("Argument xx has wrong type") from None
          else:
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
        else:
          if memview_xx.ndim != 1:
            raise TypeError("Argument xx must be one-dimensional")
          if memview_xx.format != "d":
            _tmparray_xx = array.array("d",xx)
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
      _res_putxx,_retargs_putxx = self.__obj.putxx_iO_3(whichsol,memview_xx)
      if _res_putxx != 0:
        _,_msg_putxx = self.__getlasterror(_res_putxx)
        raise Error(rescode(_res_putxx),_msg_putxx)
    def putxx(self,*args,**kwds):
      """
      Sets the xx vector for a solution.
    
      putxx(whichsol,xx)
        [whichsol : mosek.soltype]  Selects a solution.  
        [xx : array(float64)]  Primal variable solution.  
      """
      return self.__putxx_iO_3(*args,**kwds)
    def __puty_iO_3(self,whichsol,y):
      if y is None:
        raise TypeError("Argument y may not be None")
      copyback_y = False
      if y is None:
        y_ = None
        memview_y = None
      else:
        try:
          memview_y = memoryview(y)
        except TypeError:
          try:
            _tmparray_y = array.array("d",y)
          except TypeError:
            raise TypeError("Argument y has wrong type") from None
          else:
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
        else:
          if memview_y.ndim != 1:
            raise TypeError("Argument y must be one-dimensional")
          if memview_y.format != "d":
            _tmparray_y = array.array("d",y)
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
      _res_puty,_retargs_puty = self.__obj.puty_iO_3(whichsol,memview_y)
      if _res_puty != 0:
        _,_msg_puty = self.__getlasterror(_res_puty)
        raise Error(rescode(_res_puty),_msg_puty)
    def puty(self,*args,**kwds):
      """
      Sets the y vector for a solution.
    
      puty(whichsol,y)
        [whichsol : mosek.soltype]  Selects a solution.  
        [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
      """
      return self.__puty_iO_3(*args,**kwds)
    def __putslc_iO_3(self,whichsol,slc):
      if slc is None:
        raise TypeError("Argument slc may not be None")
      copyback_slc = False
      if slc is None:
        slc_ = None
        memview_slc = None
      else:
        try:
          memview_slc = memoryview(slc)
        except TypeError:
          try:
            _tmparray_slc = array.array("d",slc)
          except TypeError:
            raise TypeError("Argument slc has wrong type") from None
          else:
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
        else:
          if memview_slc.ndim != 1:
            raise TypeError("Argument slc must be one-dimensional")
          if memview_slc.format != "d":
            _tmparray_slc = array.array("d",slc)
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
      _res_putslc,_retargs_putslc = self.__obj.putslc_iO_3(whichsol,memview_slc)
      if _res_putslc != 0:
        _,_msg_putslc = self.__getlasterror(_res_putslc)
        raise Error(rescode(_res_putslc),_msg_putslc)
    def putslc(self,*args,**kwds):
      """
      Sets the slc vector for a solution.
    
      putslc(whichsol,slc)
        [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putslc_iO_3(*args,**kwds)
    def __putsuc_iO_3(self,whichsol,suc):
      if suc is None:
        raise TypeError("Argument suc may not be None")
      copyback_suc = False
      if suc is None:
        suc_ = None
        memview_suc = None
      else:
        try:
          memview_suc = memoryview(suc)
        except TypeError:
          try:
            _tmparray_suc = array.array("d",suc)
          except TypeError:
            raise TypeError("Argument suc has wrong type") from None
          else:
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
        else:
          if memview_suc.ndim != 1:
            raise TypeError("Argument suc must be one-dimensional")
          if memview_suc.format != "d":
            _tmparray_suc = array.array("d",suc)
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
      _res_putsuc,_retargs_putsuc = self.__obj.putsuc_iO_3(whichsol,memview_suc)
      if _res_putsuc != 0:
        _,_msg_putsuc = self.__getlasterror(_res_putsuc)
        raise Error(rescode(_res_putsuc),_msg_putsuc)
    def putsuc(self,*args,**kwds):
      """
      Sets the suc vector for a solution.
    
      putsuc(whichsol,suc)
        [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putsuc_iO_3(*args,**kwds)
    def __putslx_iO_3(self,whichsol,slx):
      if slx is None:
        raise TypeError("Argument slx may not be None")
      copyback_slx = False
      if slx is None:
        slx_ = None
        memview_slx = None
      else:
        try:
          memview_slx = memoryview(slx)
        except TypeError:
          try:
            _tmparray_slx = array.array("d",slx)
          except TypeError:
            raise TypeError("Argument slx has wrong type") from None
          else:
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
        else:
          if memview_slx.ndim != 1:
            raise TypeError("Argument slx must be one-dimensional")
          if memview_slx.format != "d":
            _tmparray_slx = array.array("d",slx)
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
      _res_putslx,_retargs_putslx = self.__obj.putslx_iO_3(whichsol,memview_slx)
      if _res_putslx != 0:
        _,_msg_putslx = self.__getlasterror(_res_putslx)
        raise Error(rescode(_res_putslx),_msg_putslx)
    def putslx(self,*args,**kwds):
      """
      Sets the slx vector for a solution.
    
      putslx(whichsol,slx)
        [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putslx_iO_3(*args,**kwds)
    def __putsux_iO_3(self,whichsol,sux):
      if sux is None:
        raise TypeError("Argument sux may not be None")
      copyback_sux = False
      if sux is None:
        sux_ = None
        memview_sux = None
      else:
        try:
          memview_sux = memoryview(sux)
        except TypeError:
          try:
            _tmparray_sux = array.array("d",sux)
          except TypeError:
            raise TypeError("Argument sux has wrong type") from None
          else:
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
        else:
          if memview_sux.ndim != 1:
            raise TypeError("Argument sux must be one-dimensional")
          if memview_sux.format != "d":
            _tmparray_sux = array.array("d",sux)
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
      _res_putsux,_retargs_putsux = self.__obj.putsux_iO_3(whichsol,memview_sux)
      if _res_putsux != 0:
        _,_msg_putsux = self.__getlasterror(_res_putsux)
        raise Error(rescode(_res_putsux),_msg_putsux)
    def putsux(self,*args,**kwds):
      """
      Sets the sux vector for a solution.
    
      putsux(whichsol,sux)
        [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putsux_iO_3(*args,**kwds)
    def __putsnx_iO_3(self,whichsol,sux):
      if sux is None:
        raise TypeError("Argument sux may not be None")
      copyback_sux = False
      if sux is None:
        sux_ = None
        memview_sux = None
      else:
        try:
          memview_sux = memoryview(sux)
        except TypeError:
          try:
            _tmparray_sux = array.array("d",sux)
          except TypeError:
            raise TypeError("Argument sux has wrong type") from None
          else:
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
        else:
          if memview_sux.ndim != 1:
            raise TypeError("Argument sux must be one-dimensional")
          if memview_sux.format != "d":
            _tmparray_sux = array.array("d",sux)
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
      _res_putsnx,_retargs_putsnx = self.__obj.putsnx_iO_3(whichsol,memview_sux)
      if _res_putsnx != 0:
        _,_msg_putsnx = self.__getlasterror(_res_putsnx)
        raise Error(rescode(_res_putsnx),_msg_putsnx)
    def putsnx(self,*args,**kwds):
      """
      Sets the snx vector for a solution.
    
      putsnx(whichsol,sux)
        [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putsnx_iO_3(*args,**kwds)
    def __putaccdoty_iLO_4(self,whichsol,accidx,doty):
      if doty is None:
        raise TypeError("Argument doty may not be None")
      copyback_doty = False
      if doty is None:
        doty_ = None
        memview_doty = None
      else:
        try:
          memview_doty = memoryview(doty)
        except TypeError:
          try:
            _tmparray_doty = array.array("d",[0 for _ in range(len(doty))])
          except TypeError:
            raise TypeError("Argument doty has wrong type") from None
          else:
            memview_doty = memoryview(_tmparray_doty)
            copyback_doty = True
            doty_ = _tmparray_doty
        else:
          if memview_doty.ndim != 1:
            raise TypeError("Argument doty must be one-dimensional")
          if memview_doty.format != "d":
            _tmparray_doty = array.array("d",doty)
            memview_doty = memoryview(_tmparray_doty)
            copyback_doty = True
            doty_ = _tmparray_doty
      _res_putaccdoty,_retargs_putaccdoty = self.__obj.putaccdoty_iLO_4(whichsol,accidx,memview_doty)
      if _res_putaccdoty != 0:
        _,_msg_putaccdoty = self.__getlasterror(_res_putaccdoty)
        raise Error(rescode(_res_putaccdoty),_msg_putaccdoty)
      if copyback_doty:
        for __tmp_674 in range(len(doty)): doty[__tmp_674] = doty_[__tmp_674]
    def __putaccdoty_iLO_3(self,whichsol,accidx):
      doty_ = bytearray(0)
      _res_putaccdoty,_retargs_putaccdoty = self.__obj.putaccdoty_iLO_3(whichsol,accidx,doty_)
      if _res_putaccdoty != 0:
        _,_msg_putaccdoty = self.__getlasterror(_res_putaccdoty)
        raise Error(rescode(_res_putaccdoty),_msg_putaccdoty)
      doty = array.array("d")
      doty.frombytes(doty_)
      return (doty)
    def putaccdoty(self,*args,**kwds):
      """
      Puts the doty vector for a solution.
    
      putaccdoty(whichsol,accidx,doty)
      putaccdoty(whichsol,accidx) -> (doty)
        [accidx : int64]  The index of the affine conic constraint.  
        [doty : array(float64)]  The dual values for this affine conic constraint. The array should have length equal to the dimension of the constraint.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__putaccdoty_iLO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__putaccdoty_iLO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __putskcslice_iiiO_5(self,whichsol,first,last,skc):
      if skc is None:
        skc_ = None
      else:
        # i
        _tmparray_skc_ = array.array("i",skc)
        skc_ = memoryview(_tmparray_skc_)
      _res_putskcslice,_retargs_putskcslice = self.__obj.putskcslice_iiiO_5(whichsol,first,last,skc_)
      if _res_putskcslice != 0:
        _,_msg_putskcslice = self.__getlasterror(_res_putskcslice)
        raise Error(rescode(_res_putskcslice),_msg_putskcslice)
    def putskcslice(self,*args,**kwds):
      """
      Sets the status keys for a slice of the constraints.
    
      putskcslice(whichsol,first,last,skc)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [skc : array(mosek.stakey)]  Status keys for the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putskcslice_iiiO_5(*args,**kwds)
    def __putskxslice_iiiO_5(self,whichsol,first,last,skx):
      if skx is None:
        skx_ = None
      else:
        # i
        _tmparray_skx_ = array.array("i",skx)
        skx_ = memoryview(_tmparray_skx_)
      _res_putskxslice,_retargs_putskxslice = self.__obj.putskxslice_iiiO_5(whichsol,first,last,skx_)
      if _res_putskxslice != 0:
        _,_msg_putskxslice = self.__getlasterror(_res_putskxslice)
        raise Error(rescode(_res_putskxslice),_msg_putskxslice)
    def putskxslice(self,*args,**kwds):
      """
      Sets the status keys for a slice of the variables.
    
      putskxslice(whichsol,first,last,skx)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [skx : array(mosek.stakey)]  Status keys for the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putskxslice_iiiO_5(*args,**kwds)
    def __putxcslice_iiiO_5(self,whichsol,first,last,xc):
      if xc is None:
        raise TypeError("Argument xc may not be None")
      copyback_xc = False
      if xc is None:
        xc_ = None
        memview_xc = None
      else:
        try:
          memview_xc = memoryview(xc)
        except TypeError:
          try:
            _tmparray_xc = array.array("d",xc)
          except TypeError:
            raise TypeError("Argument xc has wrong type") from None
          else:
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
        else:
          if memview_xc.ndim != 1:
            raise TypeError("Argument xc must be one-dimensional")
          if memview_xc.format != "d":
            _tmparray_xc = array.array("d",xc)
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
      _res_putxcslice,_retargs_putxcslice = self.__obj.putxcslice_iiiO_5(whichsol,first,last,memview_xc)
      if _res_putxcslice != 0:
        _,_msg_putxcslice = self.__getlasterror(_res_putxcslice)
        raise Error(rescode(_res_putxcslice),_msg_putxcslice)
    def putxcslice(self,*args,**kwds):
      """
      Sets a slice of the xc vector for a solution.
    
      putxcslice(whichsol,first,last,xc)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [xc : array(float64)]  Primal constraint solution.  
      """
      return self.__putxcslice_iiiO_5(*args,**kwds)
    def __putxxslice_iiiO_5(self,whichsol,first,last,xx):
      if xx is None:
        raise TypeError("Argument xx may not be None")
      copyback_xx = False
      if xx is None:
        xx_ = None
        memview_xx = None
      else:
        try:
          memview_xx = memoryview(xx)
        except TypeError:
          try:
            _tmparray_xx = array.array("d",xx)
          except TypeError:
            raise TypeError("Argument xx has wrong type") from None
          else:
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
        else:
          if memview_xx.ndim != 1:
            raise TypeError("Argument xx must be one-dimensional")
          if memview_xx.format != "d":
            _tmparray_xx = array.array("d",xx)
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
      _res_putxxslice,_retargs_putxxslice = self.__obj.putxxslice_iiiO_5(whichsol,first,last,memview_xx)
      if _res_putxxslice != 0:
        _,_msg_putxxslice = self.__getlasterror(_res_putxxslice)
        raise Error(rescode(_res_putxxslice),_msg_putxxslice)
    def putxxslice(self,*args,**kwds):
      """
      Sets a slice of the xx vector for a solution.
    
      putxxslice(whichsol,first,last,xx)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [xx : array(float64)]  Primal variable solution.  
      """
      return self.__putxxslice_iiiO_5(*args,**kwds)
    def __putyslice_iiiO_5(self,whichsol,first,last,y):
      if y is None:
        raise TypeError("Argument y may not be None")
      copyback_y = False
      if y is None:
        y_ = None
        memview_y = None
      else:
        try:
          memview_y = memoryview(y)
        except TypeError:
          try:
            _tmparray_y = array.array("d",y)
          except TypeError:
            raise TypeError("Argument y has wrong type") from None
          else:
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
        else:
          if memview_y.ndim != 1:
            raise TypeError("Argument y must be one-dimensional")
          if memview_y.format != "d":
            _tmparray_y = array.array("d",y)
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
      _res_putyslice,_retargs_putyslice = self.__obj.putyslice_iiiO_5(whichsol,first,last,memview_y)
      if _res_putyslice != 0:
        _,_msg_putyslice = self.__getlasterror(_res_putyslice)
        raise Error(rescode(_res_putyslice),_msg_putyslice)
    def putyslice(self,*args,**kwds):
      """
      Sets a slice of the y vector for a solution.
    
      putyslice(whichsol,first,last,y)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
      """
      return self.__putyslice_iiiO_5(*args,**kwds)
    def __putslcslice_iiiO_5(self,whichsol,first,last,slc):
      if slc is None:
        raise TypeError("Argument slc may not be None")
      copyback_slc = False
      if slc is None:
        slc_ = None
        memview_slc = None
      else:
        try:
          memview_slc = memoryview(slc)
        except TypeError:
          try:
            _tmparray_slc = array.array("d",slc)
          except TypeError:
            raise TypeError("Argument slc has wrong type") from None
          else:
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
        else:
          if memview_slc.ndim != 1:
            raise TypeError("Argument slc must be one-dimensional")
          if memview_slc.format != "d":
            _tmparray_slc = array.array("d",slc)
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
      _res_putslcslice,_retargs_putslcslice = self.__obj.putslcslice_iiiO_5(whichsol,first,last,memview_slc)
      if _res_putslcslice != 0:
        _,_msg_putslcslice = self.__getlasterror(_res_putslcslice)
        raise Error(rescode(_res_putslcslice),_msg_putslcslice)
    def putslcslice(self,*args,**kwds):
      """
      Sets a slice of the slc vector for a solution.
    
      putslcslice(whichsol,first,last,slc)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putslcslice_iiiO_5(*args,**kwds)
    def __putsucslice_iiiO_5(self,whichsol,first,last,suc):
      if suc is None:
        raise TypeError("Argument suc may not be None")
      copyback_suc = False
      if suc is None:
        suc_ = None
        memview_suc = None
      else:
        try:
          memview_suc = memoryview(suc)
        except TypeError:
          try:
            _tmparray_suc = array.array("d",suc)
          except TypeError:
            raise TypeError("Argument suc has wrong type") from None
          else:
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
        else:
          if memview_suc.ndim != 1:
            raise TypeError("Argument suc must be one-dimensional")
          if memview_suc.format != "d":
            _tmparray_suc = array.array("d",suc)
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
      _res_putsucslice,_retargs_putsucslice = self.__obj.putsucslice_iiiO_5(whichsol,first,last,memview_suc)
      if _res_putsucslice != 0:
        _,_msg_putsucslice = self.__getlasterror(_res_putsucslice)
        raise Error(rescode(_res_putsucslice),_msg_putsucslice)
    def putsucslice(self,*args,**kwds):
      """
      Sets a slice of the suc vector for a solution.
    
      putsucslice(whichsol,first,last,suc)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putsucslice_iiiO_5(*args,**kwds)
    def __putslxslice_iiiO_5(self,whichsol,first,last,slx):
      if slx is None:
        raise TypeError("Argument slx may not be None")
      copyback_slx = False
      if slx is None:
        slx_ = None
        memview_slx = None
      else:
        try:
          memview_slx = memoryview(slx)
        except TypeError:
          try:
            _tmparray_slx = array.array("d",slx)
          except TypeError:
            raise TypeError("Argument slx has wrong type") from None
          else:
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
        else:
          if memview_slx.ndim != 1:
            raise TypeError("Argument slx must be one-dimensional")
          if memview_slx.format != "d":
            _tmparray_slx = array.array("d",slx)
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
      _res_putslxslice,_retargs_putslxslice = self.__obj.putslxslice_iiiO_5(whichsol,first,last,memview_slx)
      if _res_putslxslice != 0:
        _,_msg_putslxslice = self.__getlasterror(_res_putslxslice)
        raise Error(rescode(_res_putslxslice),_msg_putslxslice)
    def putslxslice(self,*args,**kwds):
      """
      Sets a slice of the slx vector for a solution.
    
      putslxslice(whichsol,first,last,slx)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putslxslice_iiiO_5(*args,**kwds)
    def __putsuxslice_iiiO_5(self,whichsol,first,last,sux):
      if sux is None:
        raise TypeError("Argument sux may not be None")
      copyback_sux = False
      if sux is None:
        sux_ = None
        memview_sux = None
      else:
        try:
          memview_sux = memoryview(sux)
        except TypeError:
          try:
            _tmparray_sux = array.array("d",sux)
          except TypeError:
            raise TypeError("Argument sux has wrong type") from None
          else:
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
        else:
          if memview_sux.ndim != 1:
            raise TypeError("Argument sux must be one-dimensional")
          if memview_sux.format != "d":
            _tmparray_sux = array.array("d",sux)
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
      _res_putsuxslice,_retargs_putsuxslice = self.__obj.putsuxslice_iiiO_5(whichsol,first,last,memview_sux)
      if _res_putsuxslice != 0:
        _,_msg_putsuxslice = self.__getlasterror(_res_putsuxslice)
        raise Error(rescode(_res_putsuxslice),_msg_putsuxslice)
    def putsuxslice(self,*args,**kwds):
      """
      Sets a slice of the sux vector for a solution.
    
      putsuxslice(whichsol,first,last,sux)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putsuxslice_iiiO_5(*args,**kwds)
    def __putsnxslice_iiiO_5(self,whichsol,first,last,snx):
      if snx is None:
        raise TypeError("Argument snx may not be None")
      copyback_snx = False
      if snx is None:
        snx_ = None
        memview_snx = None
      else:
        try:
          memview_snx = memoryview(snx)
        except TypeError:
          try:
            _tmparray_snx = array.array("d",snx)
          except TypeError:
            raise TypeError("Argument snx has wrong type") from None
          else:
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
        else:
          if memview_snx.ndim != 1:
            raise TypeError("Argument snx must be one-dimensional")
          if memview_snx.format != "d":
            _tmparray_snx = array.array("d",snx)
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
      _res_putsnxslice,_retargs_putsnxslice = self.__obj.putsnxslice_iiiO_5(whichsol,first,last,memview_snx)
      if _res_putsnxslice != 0:
        _,_msg_putsnxslice = self.__getlasterror(_res_putsnxslice)
        raise Error(rescode(_res_putsnxslice),_msg_putsnxslice)
    def putsnxslice(self,*args,**kwds):
      """
      Sets a slice of the snx vector for a solution.
    
      putsnxslice(whichsol,first,last,snx)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putsnxslice_iiiO_5(*args,**kwds)
    def __putbarxj_iiO_4(self,whichsol,j,barxj):
      if barxj is None:
        raise TypeError("Argument barxj may not be None")
      copyback_barxj = False
      if barxj is None:
        barxj_ = None
        memview_barxj = None
      else:
        try:
          memview_barxj = memoryview(barxj)
        except TypeError:
          try:
            _tmparray_barxj = array.array("d",barxj)
          except TypeError:
            raise TypeError("Argument barxj has wrong type") from None
          else:
            memview_barxj = memoryview(_tmparray_barxj)
            copyback_barxj = True
            barxj_ = _tmparray_barxj
        else:
          if memview_barxj.ndim != 1:
            raise TypeError("Argument barxj must be one-dimensional")
          if memview_barxj.format != "d":
            _tmparray_barxj = array.array("d",barxj)
            memview_barxj = memoryview(_tmparray_barxj)
            copyback_barxj = True
            barxj_ = _tmparray_barxj
      _res_putbarxj,_retargs_putbarxj = self.__obj.putbarxj_iiO_4(whichsol,j,memview_barxj)
      if _res_putbarxj != 0:
        _,_msg_putbarxj = self.__getlasterror(_res_putbarxj)
        raise Error(rescode(_res_putbarxj),_msg_putbarxj)
    def putbarxj(self,*args,**kwds):
      """
      Sets the primal solution for a semidefinite variable.
    
      putbarxj(whichsol,j,barxj)
        [barxj : array(float64)]  Value of the j'th variable of barx.  
        [j : int32]  Index of the semidefinite variable.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putbarxj_iiO_4(*args,**kwds)
    def __putbarsj_iiO_4(self,whichsol,j,barsj):
      if barsj is None:
        raise TypeError("Argument barsj may not be None")
      copyback_barsj = False
      if barsj is None:
        barsj_ = None
        memview_barsj = None
      else:
        try:
          memview_barsj = memoryview(barsj)
        except TypeError:
          try:
            _tmparray_barsj = array.array("d",barsj)
          except TypeError:
            raise TypeError("Argument barsj has wrong type") from None
          else:
            memview_barsj = memoryview(_tmparray_barsj)
            copyback_barsj = True
            barsj_ = _tmparray_barsj
        else:
          if memview_barsj.ndim != 1:
            raise TypeError("Argument barsj must be one-dimensional")
          if memview_barsj.format != "d":
            _tmparray_barsj = array.array("d",barsj)
            memview_barsj = memoryview(_tmparray_barsj)
            copyback_barsj = True
            barsj_ = _tmparray_barsj
      _res_putbarsj,_retargs_putbarsj = self.__obj.putbarsj_iiO_4(whichsol,j,memview_barsj)
      if _res_putbarsj != 0:
        _,_msg_putbarsj = self.__getlasterror(_res_putbarsj)
        raise Error(rescode(_res_putbarsj),_msg_putbarsj)
    def putbarsj(self,*args,**kwds):
      """
      Sets the dual solution for a semidefinite variable.
    
      putbarsj(whichsol,j,barsj)
        [barsj : array(float64)]  Value of the j'th variable of barx.  
        [j : int32]  Index of the semidefinite variable.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__putbarsj_iiO_4(*args,**kwds)
    def __getpviolcon_iOO_4(self,whichsol,sub,viol):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if viol is None:
        raise TypeError("Argument viol may not be None")
      copyback_viol = False
      if viol is None:
        viol_ = None
        memview_viol = None
      else:
        try:
          memview_viol = memoryview(viol)
        except TypeError:
          try:
            _tmparray_viol = array.array("d",[0 for _ in range(len(viol))])
          except TypeError:
            raise TypeError("Argument viol has wrong type") from None
          else:
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
        else:
          if memview_viol.ndim != 1:
            raise TypeError("Argument viol must be one-dimensional")
          if memview_viol.format != "d":
            _tmparray_viol = array.array("d",viol)
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
      _res_getpviolcon,_retargs_getpviolcon = self.__obj.getpviolcon_iOO_4(whichsol,memview_sub,memview_viol)
      if _res_getpviolcon != 0:
        _,_msg_getpviolcon = self.__getlasterror(_res_getpviolcon)
        raise Error(rescode(_res_getpviolcon),_msg_getpviolcon)
      if copyback_viol:
        for __tmp_711 in range(len(viol)): viol[__tmp_711] = viol_[__tmp_711]
    def __getpviolcon_iOO_3(self,whichsol,sub):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      viol_ = bytearray(0)
      _res_getpviolcon,_retargs_getpviolcon = self.__obj.getpviolcon_iOO_3(whichsol,memview_sub,viol_)
      if _res_getpviolcon != 0:
        _,_msg_getpviolcon = self.__getlasterror(_res_getpviolcon)
        raise Error(rescode(_res_getpviolcon),_msg_getpviolcon)
      viol = array.array("d")
      viol.frombytes(viol_)
      return (viol)
    def getpviolcon(self,*args,**kwds):
      """
      Computes the violation of a primal solution associated to a constraint.
    
      getpviolcon(whichsol,sub,viol)
      getpviolcon(whichsol,sub) -> (viol)
        [sub : array(int32)]  An array of indexes of constraints.  
        [viol : array(float64)]  List of violations corresponding to sub.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getpviolcon_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getpviolcon_iOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getpviolvar_iOO_4(self,whichsol,sub,viol):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if viol is None:
        raise TypeError("Argument viol may not be None")
      copyback_viol = False
      if viol is None:
        viol_ = None
        memview_viol = None
      else:
        try:
          memview_viol = memoryview(viol)
        except TypeError:
          try:
            _tmparray_viol = array.array("d",[0 for _ in range(len(viol))])
          except TypeError:
            raise TypeError("Argument viol has wrong type") from None
          else:
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
        else:
          if memview_viol.ndim != 1:
            raise TypeError("Argument viol must be one-dimensional")
          if memview_viol.format != "d":
            _tmparray_viol = array.array("d",viol)
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
      _res_getpviolvar,_retargs_getpviolvar = self.__obj.getpviolvar_iOO_4(whichsol,memview_sub,memview_viol)
      if _res_getpviolvar != 0:
        _,_msg_getpviolvar = self.__getlasterror(_res_getpviolvar)
        raise Error(rescode(_res_getpviolvar),_msg_getpviolvar)
      if copyback_viol:
        for __tmp_715 in range(len(viol)): viol[__tmp_715] = viol_[__tmp_715]
    def __getpviolvar_iOO_3(self,whichsol,sub):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      viol_ = bytearray(0)
      _res_getpviolvar,_retargs_getpviolvar = self.__obj.getpviolvar_iOO_3(whichsol,memview_sub,viol_)
      if _res_getpviolvar != 0:
        _,_msg_getpviolvar = self.__getlasterror(_res_getpviolvar)
        raise Error(rescode(_res_getpviolvar),_msg_getpviolvar)
      viol = array.array("d")
      viol.frombytes(viol_)
      return (viol)
    def getpviolvar(self,*args,**kwds):
      """
      Computes the violation of a primal solution for a list of scalar variables.
    
      getpviolvar(whichsol,sub,viol)
      getpviolvar(whichsol,sub) -> (viol)
        [sub : array(int32)]  An array of indexes of x variables.  
        [viol : array(float64)]  List of violations corresponding to sub.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getpviolvar_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getpviolvar_iOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getpviolbarvar_iOO_4(self,whichsol,sub,viol):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if viol is None:
        raise TypeError("Argument viol may not be None")
      copyback_viol = False
      if viol is None:
        viol_ = None
        memview_viol = None
      else:
        try:
          memview_viol = memoryview(viol)
        except TypeError:
          try:
            _tmparray_viol = array.array("d",[0 for _ in range(len(viol))])
          except TypeError:
            raise TypeError("Argument viol has wrong type") from None
          else:
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
        else:
          if memview_viol.ndim != 1:
            raise TypeError("Argument viol must be one-dimensional")
          if memview_viol.format != "d":
            _tmparray_viol = array.array("d",viol)
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
      _res_getpviolbarvar,_retargs_getpviolbarvar = self.__obj.getpviolbarvar_iOO_4(whichsol,memview_sub,memview_viol)
      if _res_getpviolbarvar != 0:
        _,_msg_getpviolbarvar = self.__getlasterror(_res_getpviolbarvar)
        raise Error(rescode(_res_getpviolbarvar),_msg_getpviolbarvar)
      if copyback_viol:
        for __tmp_719 in range(len(viol)): viol[__tmp_719] = viol_[__tmp_719]
    def __getpviolbarvar_iOO_3(self,whichsol,sub):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      viol_ = bytearray(0)
      _res_getpviolbarvar,_retargs_getpviolbarvar = self.__obj.getpviolbarvar_iOO_3(whichsol,memview_sub,viol_)
      if _res_getpviolbarvar != 0:
        _,_msg_getpviolbarvar = self.__getlasterror(_res_getpviolbarvar)
        raise Error(rescode(_res_getpviolbarvar),_msg_getpviolbarvar)
      viol = array.array("d")
      viol.frombytes(viol_)
      return (viol)
    def getpviolbarvar(self,*args,**kwds):
      """
      Computes the violation of a primal solution for a list of semidefinite variables.
    
      getpviolbarvar(whichsol,sub,viol)
      getpviolbarvar(whichsol,sub) -> (viol)
        [sub : array(int32)]  An array of indexes of barX variables.  
        [viol : array(float64)]  List of violations corresponding to sub.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getpviolbarvar_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getpviolbarvar_iOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getpviolcones_iOO_4(self,whichsol,sub,viol):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if viol is None:
        raise TypeError("Argument viol may not be None")
      copyback_viol = False
      if viol is None:
        viol_ = None
        memview_viol = None
      else:
        try:
          memview_viol = memoryview(viol)
        except TypeError:
          try:
            _tmparray_viol = array.array("d",[0 for _ in range(len(viol))])
          except TypeError:
            raise TypeError("Argument viol has wrong type") from None
          else:
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
        else:
          if memview_viol.ndim != 1:
            raise TypeError("Argument viol must be one-dimensional")
          if memview_viol.format != "d":
            _tmparray_viol = array.array("d",viol)
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
      _res_getpviolcones,_retargs_getpviolcones = self.__obj.getpviolcones_iOO_4(whichsol,memview_sub,memview_viol)
      if _res_getpviolcones != 0:
        _,_msg_getpviolcones = self.__getlasterror(_res_getpviolcones)
        raise Error(rescode(_res_getpviolcones),_msg_getpviolcones)
      if copyback_viol:
        for __tmp_723 in range(len(viol)): viol[__tmp_723] = viol_[__tmp_723]
    def __getpviolcones_iOO_3(self,whichsol,sub):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      viol_ = bytearray(0)
      _res_getpviolcones,_retargs_getpviolcones = self.__obj.getpviolcones_iOO_3(whichsol,memview_sub,viol_)
      if _res_getpviolcones != 0:
        _,_msg_getpviolcones = self.__getlasterror(_res_getpviolcones)
        raise Error(rescode(_res_getpviolcones),_msg_getpviolcones)
      viol = array.array("d")
      viol.frombytes(viol_)
      return (viol)
    def getpviolcones(self,*args,**kwds):
      """
      Computes the violation of a solution for set of conic constraints.
    
      getpviolcones(whichsol,sub,viol)
      getpviolcones(whichsol,sub) -> (viol)
        [sub : array(int32)]  An array of indexes of conic constraints.  
        [viol : array(float64)]  List of violations corresponding to sub.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getpviolcones_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getpviolcones_iOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getpviolacc_iOO_4(self,whichsol,accidxlist,viol):
      if accidxlist is None:
        raise TypeError("Argument accidxlist may not be None")
      copyback_accidxlist = False
      if accidxlist is None:
        accidxlist_ = None
        memview_accidxlist = None
      else:
        try:
          memview_accidxlist = memoryview(accidxlist)
        except TypeError:
          try:
            _tmparray_accidxlist = array.array("q",accidxlist)
          except TypeError:
            raise TypeError("Argument accidxlist has wrong type") from None
          else:
            memview_accidxlist = memoryview(_tmparray_accidxlist)
            copyback_accidxlist = True
            accidxlist_ = _tmparray_accidxlist
        else:
          if memview_accidxlist.ndim != 1:
            raise TypeError("Argument accidxlist must be one-dimensional")
          if memview_accidxlist.format != "q":
            _tmparray_accidxlist = array.array("q",accidxlist)
            memview_accidxlist = memoryview(_tmparray_accidxlist)
            copyback_accidxlist = True
            accidxlist_ = _tmparray_accidxlist
      if viol is None:
        raise TypeError("Argument viol may not be None")
      copyback_viol = False
      if viol is None:
        viol_ = None
        memview_viol = None
      else:
        try:
          memview_viol = memoryview(viol)
        except TypeError:
          try:
            _tmparray_viol = array.array("d",[0 for _ in range(len(viol))])
          except TypeError:
            raise TypeError("Argument viol has wrong type") from None
          else:
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
        else:
          if memview_viol.ndim != 1:
            raise TypeError("Argument viol must be one-dimensional")
          if memview_viol.format != "d":
            _tmparray_viol = array.array("d",viol)
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
      _res_getpviolacc,_retargs_getpviolacc = self.__obj.getpviolacc_iOO_4(whichsol,memview_accidxlist,memview_viol)
      if _res_getpviolacc != 0:
        _,_msg_getpviolacc = self.__getlasterror(_res_getpviolacc)
        raise Error(rescode(_res_getpviolacc),_msg_getpviolacc)
      if copyback_viol:
        for __tmp_727 in range(len(viol)): viol[__tmp_727] = viol_[__tmp_727]
    def __getpviolacc_iOO_3(self,whichsol,accidxlist):
      if accidxlist is None:
        raise TypeError("Argument accidxlist may not be None")
      copyback_accidxlist = False
      if accidxlist is None:
        accidxlist_ = None
        memview_accidxlist = None
      else:
        try:
          memview_accidxlist = memoryview(accidxlist)
        except TypeError:
          try:
            _tmparray_accidxlist = array.array("q",accidxlist)
          except TypeError:
            raise TypeError("Argument accidxlist has wrong type") from None
          else:
            memview_accidxlist = memoryview(_tmparray_accidxlist)
            copyback_accidxlist = True
            accidxlist_ = _tmparray_accidxlist
        else:
          if memview_accidxlist.ndim != 1:
            raise TypeError("Argument accidxlist must be one-dimensional")
          if memview_accidxlist.format != "q":
            _tmparray_accidxlist = array.array("q",accidxlist)
            memview_accidxlist = memoryview(_tmparray_accidxlist)
            copyback_accidxlist = True
            accidxlist_ = _tmparray_accidxlist
      viol_ = bytearray(0)
      _res_getpviolacc,_retargs_getpviolacc = self.__obj.getpviolacc_iOO_3(whichsol,memview_accidxlist,viol_)
      if _res_getpviolacc != 0:
        _,_msg_getpviolacc = self.__getlasterror(_res_getpviolacc)
        raise Error(rescode(_res_getpviolacc),_msg_getpviolacc)
      viol = array.array("d")
      viol.frombytes(viol_)
      return (viol)
    def getpviolacc(self,*args,**kwds):
      """
      Computes the violation of a solution for set of affine conic constraints.
    
      getpviolacc(whichsol,accidxlist,viol)
      getpviolacc(whichsol,accidxlist) -> (viol)
        [accidxlist : array(int64)]  An array of indexes of conic constraints.  
        [viol : array(float64)]  List of violations corresponding to sub.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getpviolacc_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getpviolacc_iOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getpvioldjc_iOO_4(self,whichsol,djcidxlist,viol):
      if djcidxlist is None:
        raise TypeError("Argument djcidxlist may not be None")
      copyback_djcidxlist = False
      if djcidxlist is None:
        djcidxlist_ = None
        memview_djcidxlist = None
      else:
        try:
          memview_djcidxlist = memoryview(djcidxlist)
        except TypeError:
          try:
            _tmparray_djcidxlist = array.array("q",djcidxlist)
          except TypeError:
            raise TypeError("Argument djcidxlist has wrong type") from None
          else:
            memview_djcidxlist = memoryview(_tmparray_djcidxlist)
            copyback_djcidxlist = True
            djcidxlist_ = _tmparray_djcidxlist
        else:
          if memview_djcidxlist.ndim != 1:
            raise TypeError("Argument djcidxlist must be one-dimensional")
          if memview_djcidxlist.format != "q":
            _tmparray_djcidxlist = array.array("q",djcidxlist)
            memview_djcidxlist = memoryview(_tmparray_djcidxlist)
            copyback_djcidxlist = True
            djcidxlist_ = _tmparray_djcidxlist
      if viol is None:
        raise TypeError("Argument viol may not be None")
      copyback_viol = False
      if viol is None:
        viol_ = None
        memview_viol = None
      else:
        try:
          memview_viol = memoryview(viol)
        except TypeError:
          try:
            _tmparray_viol = array.array("d",[0 for _ in range(len(viol))])
          except TypeError:
            raise TypeError("Argument viol has wrong type") from None
          else:
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
        else:
          if memview_viol.ndim != 1:
            raise TypeError("Argument viol must be one-dimensional")
          if memview_viol.format != "d":
            _tmparray_viol = array.array("d",viol)
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
      _res_getpvioldjc,_retargs_getpvioldjc = self.__obj.getpvioldjc_iOO_4(whichsol,memview_djcidxlist,memview_viol)
      if _res_getpvioldjc != 0:
        _,_msg_getpvioldjc = self.__getlasterror(_res_getpvioldjc)
        raise Error(rescode(_res_getpvioldjc),_msg_getpvioldjc)
      if copyback_viol:
        for __tmp_731 in range(len(viol)): viol[__tmp_731] = viol_[__tmp_731]
    def __getpvioldjc_iOO_3(self,whichsol,djcidxlist):
      if djcidxlist is None:
        raise TypeError("Argument djcidxlist may not be None")
      copyback_djcidxlist = False
      if djcidxlist is None:
        djcidxlist_ = None
        memview_djcidxlist = None
      else:
        try:
          memview_djcidxlist = memoryview(djcidxlist)
        except TypeError:
          try:
            _tmparray_djcidxlist = array.array("q",djcidxlist)
          except TypeError:
            raise TypeError("Argument djcidxlist has wrong type") from None
          else:
            memview_djcidxlist = memoryview(_tmparray_djcidxlist)
            copyback_djcidxlist = True
            djcidxlist_ = _tmparray_djcidxlist
        else:
          if memview_djcidxlist.ndim != 1:
            raise TypeError("Argument djcidxlist must be one-dimensional")
          if memview_djcidxlist.format != "q":
            _tmparray_djcidxlist = array.array("q",djcidxlist)
            memview_djcidxlist = memoryview(_tmparray_djcidxlist)
            copyback_djcidxlist = True
            djcidxlist_ = _tmparray_djcidxlist
      viol_ = bytearray(0)
      _res_getpvioldjc,_retargs_getpvioldjc = self.__obj.getpvioldjc_iOO_3(whichsol,memview_djcidxlist,viol_)
      if _res_getpvioldjc != 0:
        _,_msg_getpvioldjc = self.__getlasterror(_res_getpvioldjc)
        raise Error(rescode(_res_getpvioldjc),_msg_getpvioldjc)
      viol = array.array("d")
      viol.frombytes(viol_)
      return (viol)
    def getpvioldjc(self,*args,**kwds):
      """
      Computes the violation of a solution for set of disjunctive constraints.
    
      getpvioldjc(whichsol,djcidxlist,viol)
      getpvioldjc(whichsol,djcidxlist) -> (viol)
        [djcidxlist : array(int64)]  An array of indexes of disjunctive constraints.  
        [viol : array(float64)]  List of violations corresponding to sub.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getpvioldjc_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getpvioldjc_iOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getdviolcon_iOO_4(self,whichsol,sub,viol):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if viol is None:
        raise TypeError("Argument viol may not be None")
      copyback_viol = False
      if viol is None:
        viol_ = None
        memview_viol = None
      else:
        try:
          memview_viol = memoryview(viol)
        except TypeError:
          try:
            _tmparray_viol = array.array("d",[0 for _ in range(len(viol))])
          except TypeError:
            raise TypeError("Argument viol has wrong type") from None
          else:
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
        else:
          if memview_viol.ndim != 1:
            raise TypeError("Argument viol must be one-dimensional")
          if memview_viol.format != "d":
            _tmparray_viol = array.array("d",viol)
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
      _res_getdviolcon,_retargs_getdviolcon = self.__obj.getdviolcon_iOO_4(whichsol,memview_sub,memview_viol)
      if _res_getdviolcon != 0:
        _,_msg_getdviolcon = self.__getlasterror(_res_getdviolcon)
        raise Error(rescode(_res_getdviolcon),_msg_getdviolcon)
      if copyback_viol:
        for __tmp_735 in range(len(viol)): viol[__tmp_735] = viol_[__tmp_735]
    def __getdviolcon_iOO_3(self,whichsol,sub):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      viol_ = bytearray(0)
      _res_getdviolcon,_retargs_getdviolcon = self.__obj.getdviolcon_iOO_3(whichsol,memview_sub,viol_)
      if _res_getdviolcon != 0:
        _,_msg_getdviolcon = self.__getlasterror(_res_getdviolcon)
        raise Error(rescode(_res_getdviolcon),_msg_getdviolcon)
      viol = array.array("d")
      viol.frombytes(viol_)
      return (viol)
    def getdviolcon(self,*args,**kwds):
      """
      Computes the violation of a dual solution associated with a set of constraints.
    
      getdviolcon(whichsol,sub,viol)
      getdviolcon(whichsol,sub) -> (viol)
        [sub : array(int32)]  An array of indexes of constraints.  
        [viol : array(float64)]  List of violations corresponding to sub.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getdviolcon_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getdviolcon_iOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getdviolvar_iOO_4(self,whichsol,sub,viol):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if viol is None:
        raise TypeError("Argument viol may not be None")
      copyback_viol = False
      if viol is None:
        viol_ = None
        memview_viol = None
      else:
        try:
          memview_viol = memoryview(viol)
        except TypeError:
          try:
            _tmparray_viol = array.array("d",[0 for _ in range(len(viol))])
          except TypeError:
            raise TypeError("Argument viol has wrong type") from None
          else:
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
        else:
          if memview_viol.ndim != 1:
            raise TypeError("Argument viol must be one-dimensional")
          if memview_viol.format != "d":
            _tmparray_viol = array.array("d",viol)
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
      _res_getdviolvar,_retargs_getdviolvar = self.__obj.getdviolvar_iOO_4(whichsol,memview_sub,memview_viol)
      if _res_getdviolvar != 0:
        _,_msg_getdviolvar = self.__getlasterror(_res_getdviolvar)
        raise Error(rescode(_res_getdviolvar),_msg_getdviolvar)
      if copyback_viol:
        for __tmp_739 in range(len(viol)): viol[__tmp_739] = viol_[__tmp_739]
    def __getdviolvar_iOO_3(self,whichsol,sub):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      viol_ = bytearray(0)
      _res_getdviolvar,_retargs_getdviolvar = self.__obj.getdviolvar_iOO_3(whichsol,memview_sub,viol_)
      if _res_getdviolvar != 0:
        _,_msg_getdviolvar = self.__getlasterror(_res_getdviolvar)
        raise Error(rescode(_res_getdviolvar),_msg_getdviolvar)
      viol = array.array("d")
      viol.frombytes(viol_)
      return (viol)
    def getdviolvar(self,*args,**kwds):
      """
      Computes the violation of a dual solution associated with a set of scalar variables.
    
      getdviolvar(whichsol,sub,viol)
      getdviolvar(whichsol,sub) -> (viol)
        [sub : array(int32)]  An array of indexes of x variables.  
        [viol : array(float64)]  List of violations corresponding to sub.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getdviolvar_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getdviolvar_iOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getdviolbarvar_iOO_4(self,whichsol,sub,viol):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if viol is None:
        raise TypeError("Argument viol may not be None")
      copyback_viol = False
      if viol is None:
        viol_ = None
        memview_viol = None
      else:
        try:
          memview_viol = memoryview(viol)
        except TypeError:
          try:
            _tmparray_viol = array.array("d",[0 for _ in range(len(viol))])
          except TypeError:
            raise TypeError("Argument viol has wrong type") from None
          else:
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
        else:
          if memview_viol.ndim != 1:
            raise TypeError("Argument viol must be one-dimensional")
          if memview_viol.format != "d":
            _tmparray_viol = array.array("d",viol)
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
      _res_getdviolbarvar,_retargs_getdviolbarvar = self.__obj.getdviolbarvar_iOO_4(whichsol,memview_sub,memview_viol)
      if _res_getdviolbarvar != 0:
        _,_msg_getdviolbarvar = self.__getlasterror(_res_getdviolbarvar)
        raise Error(rescode(_res_getdviolbarvar),_msg_getdviolbarvar)
      if copyback_viol:
        for __tmp_743 in range(len(viol)): viol[__tmp_743] = viol_[__tmp_743]
    def __getdviolbarvar_iOO_3(self,whichsol,sub):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      viol_ = bytearray(0)
      _res_getdviolbarvar,_retargs_getdviolbarvar = self.__obj.getdviolbarvar_iOO_3(whichsol,memview_sub,viol_)
      if _res_getdviolbarvar != 0:
        _,_msg_getdviolbarvar = self.__getlasterror(_res_getdviolbarvar)
        raise Error(rescode(_res_getdviolbarvar),_msg_getdviolbarvar)
      viol = array.array("d")
      viol.frombytes(viol_)
      return (viol)
    def getdviolbarvar(self,*args,**kwds):
      """
      Computes the violation of dual solution for a set of semidefinite variables.
    
      getdviolbarvar(whichsol,sub,viol)
      getdviolbarvar(whichsol,sub) -> (viol)
        [sub : array(int32)]  An array of indexes of barx variables.  
        [viol : array(float64)]  List of violations corresponding to sub.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getdviolbarvar_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getdviolbarvar_iOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getdviolcones_iOO_4(self,whichsol,sub,viol):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if viol is None:
        raise TypeError("Argument viol may not be None")
      copyback_viol = False
      if viol is None:
        viol_ = None
        memview_viol = None
      else:
        try:
          memview_viol = memoryview(viol)
        except TypeError:
          try:
            _tmparray_viol = array.array("d",[0 for _ in range(len(viol))])
          except TypeError:
            raise TypeError("Argument viol has wrong type") from None
          else:
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
        else:
          if memview_viol.ndim != 1:
            raise TypeError("Argument viol must be one-dimensional")
          if memview_viol.format != "d":
            _tmparray_viol = array.array("d",viol)
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
      _res_getdviolcones,_retargs_getdviolcones = self.__obj.getdviolcones_iOO_4(whichsol,memview_sub,memview_viol)
      if _res_getdviolcones != 0:
        _,_msg_getdviolcones = self.__getlasterror(_res_getdviolcones)
        raise Error(rescode(_res_getdviolcones),_msg_getdviolcones)
      if copyback_viol:
        for __tmp_747 in range(len(viol)): viol[__tmp_747] = viol_[__tmp_747]
    def __getdviolcones_iOO_3(self,whichsol,sub):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      viol_ = bytearray(0)
      _res_getdviolcones,_retargs_getdviolcones = self.__obj.getdviolcones_iOO_3(whichsol,memview_sub,viol_)
      if _res_getdviolcones != 0:
        _,_msg_getdviolcones = self.__getlasterror(_res_getdviolcones)
        raise Error(rescode(_res_getdviolcones),_msg_getdviolcones)
      viol = array.array("d")
      viol.frombytes(viol_)
      return (viol)
    def getdviolcones(self,*args,**kwds):
      """
      Computes the violation of a solution for set of dual conic constraints.
    
      getdviolcones(whichsol,sub,viol)
      getdviolcones(whichsol,sub) -> (viol)
        [sub : array(int32)]  An array of indexes of conic constraints.  
        [viol : array(float64)]  List of violations corresponding to sub.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getdviolcones_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getdviolcones_iOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getdviolacc_iOO_4(self,whichsol,accidxlist,viol):
      if accidxlist is None:
        raise TypeError("Argument accidxlist may not be None")
      copyback_accidxlist = False
      if accidxlist is None:
        accidxlist_ = None
        memview_accidxlist = None
      else:
        try:
          memview_accidxlist = memoryview(accidxlist)
        except TypeError:
          try:
            _tmparray_accidxlist = array.array("q",accidxlist)
          except TypeError:
            raise TypeError("Argument accidxlist has wrong type") from None
          else:
            memview_accidxlist = memoryview(_tmparray_accidxlist)
            copyback_accidxlist = True
            accidxlist_ = _tmparray_accidxlist
        else:
          if memview_accidxlist.ndim != 1:
            raise TypeError("Argument accidxlist must be one-dimensional")
          if memview_accidxlist.format != "q":
            _tmparray_accidxlist = array.array("q",accidxlist)
            memview_accidxlist = memoryview(_tmparray_accidxlist)
            copyback_accidxlist = True
            accidxlist_ = _tmparray_accidxlist
      if viol is None:
        raise TypeError("Argument viol may not be None")
      copyback_viol = False
      if viol is None:
        viol_ = None
        memview_viol = None
      else:
        try:
          memview_viol = memoryview(viol)
        except TypeError:
          try:
            _tmparray_viol = array.array("d",[0 for _ in range(len(viol))])
          except TypeError:
            raise TypeError("Argument viol has wrong type") from None
          else:
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
        else:
          if memview_viol.ndim != 1:
            raise TypeError("Argument viol must be one-dimensional")
          if memview_viol.format != "d":
            _tmparray_viol = array.array("d",viol)
            memview_viol = memoryview(_tmparray_viol)
            copyback_viol = True
            viol_ = _tmparray_viol
      _res_getdviolacc,_retargs_getdviolacc = self.__obj.getdviolacc_iOO_4(whichsol,memview_accidxlist,memview_viol)
      if _res_getdviolacc != 0:
        _,_msg_getdviolacc = self.__getlasterror(_res_getdviolacc)
        raise Error(rescode(_res_getdviolacc),_msg_getdviolacc)
      if copyback_viol:
        for __tmp_751 in range(len(viol)): viol[__tmp_751] = viol_[__tmp_751]
    def __getdviolacc_iOO_3(self,whichsol,accidxlist):
      if accidxlist is None:
        raise TypeError("Argument accidxlist may not be None")
      copyback_accidxlist = False
      if accidxlist is None:
        accidxlist_ = None
        memview_accidxlist = None
      else:
        try:
          memview_accidxlist = memoryview(accidxlist)
        except TypeError:
          try:
            _tmparray_accidxlist = array.array("q",accidxlist)
          except TypeError:
            raise TypeError("Argument accidxlist has wrong type") from None
          else:
            memview_accidxlist = memoryview(_tmparray_accidxlist)
            copyback_accidxlist = True
            accidxlist_ = _tmparray_accidxlist
        else:
          if memview_accidxlist.ndim != 1:
            raise TypeError("Argument accidxlist must be one-dimensional")
          if memview_accidxlist.format != "q":
            _tmparray_accidxlist = array.array("q",accidxlist)
            memview_accidxlist = memoryview(_tmparray_accidxlist)
            copyback_accidxlist = True
            accidxlist_ = _tmparray_accidxlist
      viol_ = bytearray(0)
      _res_getdviolacc,_retargs_getdviolacc = self.__obj.getdviolacc_iOO_3(whichsol,memview_accidxlist,viol_)
      if _res_getdviolacc != 0:
        _,_msg_getdviolacc = self.__getlasterror(_res_getdviolacc)
        raise Error(rescode(_res_getdviolacc),_msg_getdviolacc)
      viol = array.array("d")
      viol.frombytes(viol_)
      return (viol)
    def getdviolacc(self,*args,**kwds):
      """
      Computes the violation of the dual solution for set of affine conic constraints.
    
      getdviolacc(whichsol,accidxlist,viol)
      getdviolacc(whichsol,accidxlist) -> (viol)
        [accidxlist : array(int64)]  An array of indexes of conic constraints.  
        [viol : array(float64)]  List of violations corresponding to sub.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getdviolacc_iOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getdviolacc_iOO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getsolutioninfo_i_2(self,whichsol):
      _res_getsolutioninfo,_retargs_getsolutioninfo = self.__obj.getsolutioninfo_i_2(whichsol)
      if _res_getsolutioninfo != 0:
        _,_msg_getsolutioninfo = self.__getlasterror(_res_getsolutioninfo)
        raise Error(rescode(_res_getsolutioninfo),_msg_getsolutioninfo)
      else:
        (pobj,pviolcon,pviolvar,pviolbarvar,pviolcone,pviolitg,dobj,dviolcon,dviolvar,dviolbarvar,dviolcone) = _retargs_getsolutioninfo
      return (pobj,pviolcon,pviolvar,pviolbarvar,pviolcone,pviolitg,dobj,dviolcon,dviolvar,dviolbarvar,dviolcone)
    def getsolutioninfo(self,*args,**kwds):
      """
      Obtains information about of a solution.
    
      getsolutioninfo(whichsol) -> 
                     (pobj,
                      pviolcon,
                      pviolvar,
                      pviolbarvar,
                      pviolcone,
                      pviolitg,
                      dobj,
                      dviolcon,
                      dviolvar,
                      dviolbarvar,
                      dviolcone)
        [dobj : float64]  Dual objective value.  
        [dviolbarvar : float64]  Maximal dual bound violation for a bars variable.  
        [dviolcon : float64]  Maximal dual bound violation for a xc variable.  
        [dviolcone : float64]  Maximum violation of the dual solution in the dual conic constraints.  
        [dviolvar : float64]  Maximal dual bound violation for a xx variable.  
        [pobj : float64]  The primal objective value.  
        [pviolbarvar : float64]  Maximal primal bound violation for a barx variable.  
        [pviolcon : float64]  Maximal primal bound violation for a xc variable.  
        [pviolcone : float64]  Maximal primal violation of the solution with respect to the conic constraints.  
        [pviolitg : float64]  Maximal violation in the integer constraints.  
        [pviolvar : float64]  Maximal primal bound violation for a xx variable.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__getsolutioninfo_i_2(*args,**kwds)
    def __getsolutioninfonew_i_2(self,whichsol):
      _res_getsolutioninfonew,_retargs_getsolutioninfonew = self.__obj.getsolutioninfonew_i_2(whichsol)
      if _res_getsolutioninfonew != 0:
        _,_msg_getsolutioninfonew = self.__getlasterror(_res_getsolutioninfonew)
        raise Error(rescode(_res_getsolutioninfonew),_msg_getsolutioninfonew)
      else:
        (pobj,pviolcon,pviolvar,pviolbarvar,pviolcone,pviolacc,pvioldjc,pviolitg,dobj,dviolcon,dviolvar,dviolbarvar,dviolcone,dviolacc) = _retargs_getsolutioninfonew
      return (pobj,pviolcon,pviolvar,pviolbarvar,pviolcone,pviolacc,pvioldjc,pviolitg,dobj,dviolcon,dviolvar,dviolbarvar,dviolcone,dviolacc)
    def getsolutioninfonew(self,*args,**kwds):
      """
      Obtains information about of a solution.
    
      getsolutioninfonew(whichsol) -> 
                        (pobj,
                         pviolcon,
                         pviolvar,
                         pviolbarvar,
                         pviolcone,
                         pviolacc,
                         pvioldjc,
                         pviolitg,
                         dobj,
                         dviolcon,
                         dviolvar,
                         dviolbarvar,
                         dviolcone,
                         dviolacc)
        [dobj : float64]  Dual objective value.  
        [dviolacc : float64]  Maximum violation of the dual solution in the dual affine conic constraints.  
        [dviolbarvar : float64]  Maximal dual bound violation for a bars variable.  
        [dviolcon : float64]  Maximal dual bound violation for a xc variable.  
        [dviolcone : float64]  Maximum violation of the dual solution in the dual conic constraints.  
        [dviolvar : float64]  Maximal dual bound violation for a xx variable.  
        [pobj : float64]  The primal objective value.  
        [pviolacc : float64]  Maximal primal violation of the solution with respect to the affine conic constraints.  
        [pviolbarvar : float64]  Maximal primal bound violation for a barx variable.  
        [pviolcon : float64]  Maximal primal bound violation for a xc variable.  
        [pviolcone : float64]  Maximal primal violation of the solution with respect to the conic constraints.  
        [pvioldjc : float64]  Maximal primal violation of the solution with respect to the disjunctive constraints.  
        [pviolitg : float64]  Maximal violation in the integer constraints.  
        [pviolvar : float64]  Maximal primal bound violation for a xx variable.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__getsolutioninfonew_i_2(*args,**kwds)
    def __getdualsolutionnorms_i_2(self,whichsol):
      _res_getdualsolutionnorms,_retargs_getdualsolutionnorms = self.__obj.getdualsolutionnorms_i_2(whichsol)
      if _res_getdualsolutionnorms != 0:
        _,_msg_getdualsolutionnorms = self.__getlasterror(_res_getdualsolutionnorms)
        raise Error(rescode(_res_getdualsolutionnorms),_msg_getdualsolutionnorms)
      else:
        (nrmy,nrmslc,nrmsuc,nrmslx,nrmsux,nrmsnx,nrmbars) = _retargs_getdualsolutionnorms
      return (nrmy,nrmslc,nrmsuc,nrmslx,nrmsux,nrmsnx,nrmbars)
    def getdualsolutionnorms(self,*args,**kwds):
      """
      Compute norms of the dual solution.
    
      getdualsolutionnorms(whichsol) -> 
                          (nrmy,
                           nrmslc,
                           nrmsuc,
                           nrmslx,
                           nrmsux,
                           nrmsnx,
                           nrmbars)
        [nrmbars : float64]  The norm of the bars vector.  
        [nrmslc : float64]  The norm of the slc vector.  
        [nrmslx : float64]  The norm of the slx vector.  
        [nrmsnx : float64]  The norm of the snx vector.  
        [nrmsuc : float64]  The norm of the suc vector.  
        [nrmsux : float64]  The norm of the sux vector.  
        [nrmy : float64]  The norm of the y vector.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__getdualsolutionnorms_i_2(*args,**kwds)
    def __getprimalsolutionnorms_i_2(self,whichsol):
      _res_getprimalsolutionnorms,_retargs_getprimalsolutionnorms = self.__obj.getprimalsolutionnorms_i_2(whichsol)
      if _res_getprimalsolutionnorms != 0:
        _,_msg_getprimalsolutionnorms = self.__getlasterror(_res_getprimalsolutionnorms)
        raise Error(rescode(_res_getprimalsolutionnorms),_msg_getprimalsolutionnorms)
      else:
        (nrmxc,nrmxx,nrmbarx) = _retargs_getprimalsolutionnorms
      return (nrmxc,nrmxx,nrmbarx)
    def getprimalsolutionnorms(self,*args,**kwds):
      """
      Compute norms of the primal solution.
    
      getprimalsolutionnorms(whichsol) -> (nrmxc,nrmxx,nrmbarx)
        [nrmbarx : float64]  The norm of the barX vector.  
        [nrmxc : float64]  The norm of the xc vector.  
        [nrmxx : float64]  The norm of the xx vector.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__getprimalsolutionnorms_i_2(*args,**kwds)
    def __getsolutionslice_iiiiO_6(self,whichsol,solitem,first,last,values):
      copyback_values = False
      if values is None:
        values_ = None
        memview_values = None
      else:
        try:
          memview_values = memoryview(values)
        except TypeError:
          try:
            _tmparray_values = array.array("d",[0 for _ in range(len(values))])
          except TypeError:
            raise TypeError("Argument values has wrong type") from None
          else:
            memview_values = memoryview(_tmparray_values)
            copyback_values = True
            values_ = _tmparray_values
        else:
          if memview_values.ndim != 1:
            raise TypeError("Argument values must be one-dimensional")
          if memview_values.format != "d":
            _tmparray_values = array.array("d",values)
            memview_values = memoryview(_tmparray_values)
            copyback_values = True
            values_ = _tmparray_values
      _res_getsolutionslice,_retargs_getsolutionslice = self.__obj.getsolutionslice_iiiiO_6(whichsol,solitem,first,last,memview_values)
      if _res_getsolutionslice != 0:
        _,_msg_getsolutionslice = self.__getlasterror(_res_getsolutionslice)
        raise Error(rescode(_res_getsolutionslice),_msg_getsolutionslice)
      if copyback_values:
        for __tmp_754 in range(len(values)): values[__tmp_754] = values_[__tmp_754]
    def __getsolutionslice_iiiiO_5(self,whichsol,solitem,first,last):
      values_ = bytearray(0)
      _res_getsolutionslice,_retargs_getsolutionslice = self.__obj.getsolutionslice_iiiiO_5(whichsol,solitem,first,last,values_)
      if _res_getsolutionslice != 0:
        _,_msg_getsolutionslice = self.__getlasterror(_res_getsolutionslice)
        raise Error(rescode(_res_getsolutionslice),_msg_getsolutionslice)
      values = array.array("d")
      values.frombytes(values_)
      return (values)
    def getsolutionslice(self,*args,**kwds):
      """
      Obtains a slice of the solution.
    
      getsolutionslice(whichsol,solitem,first,last,values)
      getsolutionslice(whichsol,solitem,first,last) -> (values)
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
        [solitem : mosek.solitem]  Which part of the solution is required.  
        [values : array(float64)]  The values of the requested solution elements.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__getsolutionslice_iiiiO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 5: return self.__getsolutionslice_iiiiO_5(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getreducedcosts_iiiO_5(self,whichsol,first,last,redcosts):
      copyback_redcosts = False
      if redcosts is None:
        redcosts_ = None
        memview_redcosts = None
      else:
        try:
          memview_redcosts = memoryview(redcosts)
        except TypeError:
          try:
            _tmparray_redcosts = array.array("d",[0 for _ in range(len(redcosts))])
          except TypeError:
            raise TypeError("Argument redcosts has wrong type") from None
          else:
            memview_redcosts = memoryview(_tmparray_redcosts)
            copyback_redcosts = True
            redcosts_ = _tmparray_redcosts
        else:
          if memview_redcosts.ndim != 1:
            raise TypeError("Argument redcosts must be one-dimensional")
          if memview_redcosts.format != "d":
            _tmparray_redcosts = array.array("d",redcosts)
            memview_redcosts = memoryview(_tmparray_redcosts)
            copyback_redcosts = True
            redcosts_ = _tmparray_redcosts
      _res_getreducedcosts,_retargs_getreducedcosts = self.__obj.getreducedcosts_iiiO_5(whichsol,first,last,memview_redcosts)
      if _res_getreducedcosts != 0:
        _,_msg_getreducedcosts = self.__getlasterror(_res_getreducedcosts)
        raise Error(rescode(_res_getreducedcosts),_msg_getreducedcosts)
      if copyback_redcosts:
        for __tmp_756 in range(len(redcosts)): redcosts[__tmp_756] = redcosts_[__tmp_756]
    def __getreducedcosts_iiiO_4(self,whichsol,first,last):
      redcosts_ = bytearray(0)
      _res_getreducedcosts,_retargs_getreducedcosts = self.__obj.getreducedcosts_iiiO_4(whichsol,first,last,redcosts_)
      if _res_getreducedcosts != 0:
        _,_msg_getreducedcosts = self.__getlasterror(_res_getreducedcosts)
        raise Error(rescode(_res_getreducedcosts),_msg_getreducedcosts)
      redcosts = array.array("d")
      redcosts.frombytes(redcosts_)
      return (redcosts)
    def getreducedcosts(self,*args,**kwds):
      """
      Obtains the reduced costs for a sequence of variables.
    
      getreducedcosts(whichsol,first,last,redcosts)
      getreducedcosts(whichsol,first,last) -> (redcosts)
        [first : int32]  The index of the first variable in the sequence.  
        [last : int32]  The index of the last variable in the sequence plus 1.  
        [redcosts : array(float64)]  Returns the requested reduced costs.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getreducedcosts_iiiO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 4: return self.__getreducedcosts_iiiO_4(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getstrparam_iO_2(self,param):
      parvalue = bytearray(0)
      _res_getstrparam,_retargs_getstrparam = self.__obj.getstrparam_iO_2(param,parvalue)
      if _res_getstrparam != 0:
        _,_msg_getstrparam = self.__getlasterror(_res_getstrparam)
        raise Error(rescode(_res_getstrparam),_msg_getstrparam)
      else:
        (len) = _retargs_getstrparam
      __tmp_760 = parvalue.find(b"\0")
      if __tmp_760 >= 0:
        parvalue = parvalue[:__tmp_760]
      return (len,parvalue.decode("utf-8",errors="ignore"))
    def getstrparam(self,*args,**kwds):
      """
      Obtains the value of a string parameter.
    
      getstrparam(param) -> (len,parvalue)
        [len : int32]  The length of the parameter value.  
        [param : mosek.sparam]  Which parameter.  
        [parvalue : str]  If this is not a null pointer, the parameter value is stored here.  
      """
      return self.__getstrparam_iO_2(*args,**kwds)
    def __getstrparamlen_i_2(self,param):
      _res_getstrparamlen,_retargs_getstrparamlen = self.__obj.getstrparamlen_i_2(param)
      if _res_getstrparamlen != 0:
        _,_msg_getstrparamlen = self.__getlasterror(_res_getstrparamlen)
        raise Error(rescode(_res_getstrparamlen),_msg_getstrparamlen)
      else:
        (len) = _retargs_getstrparamlen
      return (len)
    def getstrparamlen(self,*args,**kwds):
      """
      Obtains the length of a string parameter.
    
      getstrparamlen(param) -> (len)
        [len : int32]  The length of the parameter value.  
        [param : mosek.sparam]  Which parameter.  
      """
      return self.__getstrparamlen_i_2(*args,**kwds)
    def __gettasknamelen__1(self):
      _res_gettasknamelen,_retargs_gettasknamelen = self.__obj.gettasknamelen__1()
      if _res_gettasknamelen != 0:
        _,_msg_gettasknamelen = self.__getlasterror(_res_gettasknamelen)
        raise Error(rescode(_res_gettasknamelen),_msg_gettasknamelen)
      else:
        (len) = _retargs_gettasknamelen
      return (len)
    def gettasknamelen(self,*args,**kwds):
      """
      Obtains the length the task name.
    
      gettasknamelen() -> (len)
        [len : int32]  Returns the length of the task name.  
      """
      return self.__gettasknamelen__1(*args,**kwds)
    def __gettaskname_O_1(self):
      taskname = bytearray(0)
      _res_gettaskname,_retargs_gettaskname = self.__obj.gettaskname_O_1(taskname)
      if _res_gettaskname != 0:
        _,_msg_gettaskname = self.__getlasterror(_res_gettaskname)
        raise Error(rescode(_res_gettaskname),_msg_gettaskname)
      __tmp_766 = taskname.find(b"\0")
      if __tmp_766 >= 0:
        taskname = taskname[:__tmp_766]
      return (taskname.decode("utf-8",errors="ignore"))
    def gettaskname(self,*args,**kwds):
      """
      Obtains the task name.
    
      gettaskname() -> (taskname)
        [taskname : str]  Returns the task name.  
      """
      return self.__gettaskname_O_1(*args,**kwds)
    def __getvartype_i_2(self,j):
      _res_getvartype,_retargs_getvartype = self.__obj.getvartype_i_2(j)
      if _res_getvartype != 0:
        _,_msg_getvartype = self.__getlasterror(_res_getvartype)
        raise Error(rescode(_res_getvartype),_msg_getvartype)
      else:
        (vartype) = _retargs_getvartype
      return (variabletype(vartype))
    def getvartype(self,*args,**kwds):
      """
      Gets the variable type of one variable.
    
      getvartype(j) -> (vartype)
        [j : int32]  Index of the variable.  
        [vartype : mosek.variabletype]  Variable type of variable index j.  
      """
      return self.__getvartype_i_2(*args,**kwds)
    def __getvartypelist_OO_3(self,subj,vartype):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if vartype is None:
        vartype_ = None
      else:
        # o
        _tmparray_vartype_ = array.array("i",[0 for _ in range(len(vartype))])
        vartype_ = memoryview(_tmparray_vartype_)
      _res_getvartypelist,_retargs_getvartypelist = self.__obj.getvartypelist_OO_3(memview_subj,vartype_)
      if _res_getvartypelist != 0:
        _,_msg_getvartypelist = self.__getlasterror(_res_getvartypelist)
        raise Error(rescode(_res_getvartypelist),_msg_getvartypelist)
      for __tmp_771 in range(len(vartype)): vartype[__tmp_771] = variabletype(vartype_[__tmp_771])
    def __getvartypelist_OO_2(self,subj):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      vartype_ = bytearray(0)
      _res_getvartypelist,_retargs_getvartypelist = self.__obj.getvartypelist_OO_2(memview_subj,vartype_)
      if _res_getvartypelist != 0:
        _,_msg_getvartypelist = self.__getlasterror(_res_getvartypelist)
        raise Error(rescode(_res_getvartypelist),_msg_getvartypelist)
      vartype_ints = array.array("i")
      vartype_ints.frombytes(vartype_)
      vartype = [ variabletype(__tmp_773) for __tmp_773 in vartype_ints ]
      return (vartype)
    def getvartypelist(self,*args,**kwds):
      """
      Obtains the variable type for one or more variables.
    
      getvartypelist(subj,vartype)
      getvartypelist(subj) -> (vartype)
        [subj : array(int32)]  A list of variable indexes.  
        [vartype : array(mosek.variabletype)]  Returns the variables types corresponding the variable indexes requested.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getvartypelist_OO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getvartypelist_OO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __inputdata64_iiOdOOOOOOOOOO_15(self,maxnumcon,maxnumvar,c,cfix,aptrb,aptre,asub,aval,bkc,blc,buc,bkx,blx,bux):
      copyback_c = False
      if c is None:
        c_ = None
        memview_c = None
      else:
        try:
          memview_c = memoryview(c)
        except TypeError:
          try:
            _tmparray_c = array.array("d",c)
          except TypeError:
            raise TypeError("Argument c has wrong type") from None
          else:
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
        else:
          if memview_c.ndim != 1:
            raise TypeError("Argument c must be one-dimensional")
          if memview_c.format != "d":
            _tmparray_c = array.array("d",c)
            memview_c = memoryview(_tmparray_c)
            copyback_c = True
            c_ = _tmparray_c
      if aptrb is None:
        raise TypeError("Argument aptrb may not be None")
      copyback_aptrb = False
      if aptrb is None:
        aptrb_ = None
        memview_aptrb = None
      else:
        try:
          memview_aptrb = memoryview(aptrb)
        except TypeError:
          try:
            _tmparray_aptrb = array.array("q",aptrb)
          except TypeError:
            raise TypeError("Argument aptrb has wrong type") from None
          else:
            memview_aptrb = memoryview(_tmparray_aptrb)
            copyback_aptrb = True
            aptrb_ = _tmparray_aptrb
        else:
          if memview_aptrb.ndim != 1:
            raise TypeError("Argument aptrb must be one-dimensional")
          if memview_aptrb.format != "q":
            _tmparray_aptrb = array.array("q",aptrb)
            memview_aptrb = memoryview(_tmparray_aptrb)
            copyback_aptrb = True
            aptrb_ = _tmparray_aptrb
      if aptre is None:
        raise TypeError("Argument aptre may not be None")
      copyback_aptre = False
      if aptre is None:
        aptre_ = None
        memview_aptre = None
      else:
        try:
          memview_aptre = memoryview(aptre)
        except TypeError:
          try:
            _tmparray_aptre = array.array("q",aptre)
          except TypeError:
            raise TypeError("Argument aptre has wrong type") from None
          else:
            memview_aptre = memoryview(_tmparray_aptre)
            copyback_aptre = True
            aptre_ = _tmparray_aptre
        else:
          if memview_aptre.ndim != 1:
            raise TypeError("Argument aptre must be one-dimensional")
          if memview_aptre.format != "q":
            _tmparray_aptre = array.array("q",aptre)
            memview_aptre = memoryview(_tmparray_aptre)
            copyback_aptre = True
            aptre_ = _tmparray_aptre
      if asub is None:
        raise TypeError("Argument asub may not be None")
      copyback_asub = False
      if asub is None:
        asub_ = None
        memview_asub = None
      else:
        try:
          memview_asub = memoryview(asub)
        except TypeError:
          try:
            _tmparray_asub = array.array("i",asub)
          except TypeError:
            raise TypeError("Argument asub has wrong type") from None
          else:
            memview_asub = memoryview(_tmparray_asub)
            copyback_asub = True
            asub_ = _tmparray_asub
        else:
          if memview_asub.ndim != 1:
            raise TypeError("Argument asub must be one-dimensional")
          if memview_asub.format != "i":
            _tmparray_asub = array.array("i",asub)
            memview_asub = memoryview(_tmparray_asub)
            copyback_asub = True
            asub_ = _tmparray_asub
      if aval is None:
        raise TypeError("Argument aval may not be None")
      copyback_aval = False
      if aval is None:
        aval_ = None
        memview_aval = None
      else:
        try:
          memview_aval = memoryview(aval)
        except TypeError:
          try:
            _tmparray_aval = array.array("d",aval)
          except TypeError:
            raise TypeError("Argument aval has wrong type") from None
          else:
            memview_aval = memoryview(_tmparray_aval)
            copyback_aval = True
            aval_ = _tmparray_aval
        else:
          if memview_aval.ndim != 1:
            raise TypeError("Argument aval must be one-dimensional")
          if memview_aval.format != "d":
            _tmparray_aval = array.array("d",aval)
            memview_aval = memoryview(_tmparray_aval)
            copyback_aval = True
            aval_ = _tmparray_aval
      if bkc is None:
        bkc_ = None
      else:
        # i
        _tmparray_bkc_ = array.array("i",bkc)
        bkc_ = memoryview(_tmparray_bkc_)
      if blc is None:
        raise TypeError("Argument blc may not be None")
      copyback_blc = False
      if blc is None:
        blc_ = None
        memview_blc = None
      else:
        try:
          memview_blc = memoryview(blc)
        except TypeError:
          try:
            _tmparray_blc = array.array("d",blc)
          except TypeError:
            raise TypeError("Argument blc has wrong type") from None
          else:
            memview_blc = memoryview(_tmparray_blc)
            copyback_blc = True
            blc_ = _tmparray_blc
        else:
          if memview_blc.ndim != 1:
            raise TypeError("Argument blc must be one-dimensional")
          if memview_blc.format != "d":
            _tmparray_blc = array.array("d",blc)
            memview_blc = memoryview(_tmparray_blc)
            copyback_blc = True
            blc_ = _tmparray_blc
      if buc is None:
        raise TypeError("Argument buc may not be None")
      copyback_buc = False
      if buc is None:
        buc_ = None
        memview_buc = None
      else:
        try:
          memview_buc = memoryview(buc)
        except TypeError:
          try:
            _tmparray_buc = array.array("d",buc)
          except TypeError:
            raise TypeError("Argument buc has wrong type") from None
          else:
            memview_buc = memoryview(_tmparray_buc)
            copyback_buc = True
            buc_ = _tmparray_buc
        else:
          if memview_buc.ndim != 1:
            raise TypeError("Argument buc must be one-dimensional")
          if memview_buc.format != "d":
            _tmparray_buc = array.array("d",buc)
            memview_buc = memoryview(_tmparray_buc)
            copyback_buc = True
            buc_ = _tmparray_buc
      if bkx is None:
        bkx_ = None
      else:
        # i
        _tmparray_bkx_ = array.array("i",bkx)
        bkx_ = memoryview(_tmparray_bkx_)
      if blx is None:
        raise TypeError("Argument blx may not be None")
      copyback_blx = False
      if blx is None:
        blx_ = None
        memview_blx = None
      else:
        try:
          memview_blx = memoryview(blx)
        except TypeError:
          try:
            _tmparray_blx = array.array("d",blx)
          except TypeError:
            raise TypeError("Argument blx has wrong type") from None
          else:
            memview_blx = memoryview(_tmparray_blx)
            copyback_blx = True
            blx_ = _tmparray_blx
        else:
          if memview_blx.ndim != 1:
            raise TypeError("Argument blx must be one-dimensional")
          if memview_blx.format != "d":
            _tmparray_blx = array.array("d",blx)
            memview_blx = memoryview(_tmparray_blx)
            copyback_blx = True
            blx_ = _tmparray_blx
      if bux is None:
        raise TypeError("Argument bux may not be None")
      copyback_bux = False
      if bux is None:
        bux_ = None
        memview_bux = None
      else:
        try:
          memview_bux = memoryview(bux)
        except TypeError:
          try:
            _tmparray_bux = array.array("d",bux)
          except TypeError:
            raise TypeError("Argument bux has wrong type") from None
          else:
            memview_bux = memoryview(_tmparray_bux)
            copyback_bux = True
            bux_ = _tmparray_bux
        else:
          if memview_bux.ndim != 1:
            raise TypeError("Argument bux must be one-dimensional")
          if memview_bux.format != "d":
            _tmparray_bux = array.array("d",bux)
            memview_bux = memoryview(_tmparray_bux)
            copyback_bux = True
            bux_ = _tmparray_bux
      _res_inputdata64,_retargs_inputdata64 = self.__obj.inputdata64_iiOdOOOOOOOOOO_15(maxnumcon,maxnumvar,memview_c,cfix,memview_aptrb,memview_aptre,memview_asub,memview_aval,bkc_,memview_blc,memview_buc,bkx_,memview_blx,memview_bux)
      if _res_inputdata64 != 0:
        _,_msg_inputdata64 = self.__getlasterror(_res_inputdata64)
        raise Error(rescode(_res_inputdata64),_msg_inputdata64)
    def inputdata(self,*args,**kwds):
      """
      Input the linear part of an optimization task in one function call.
    
      inputdata(maxnumcon,
                maxnumvar,
                c,
                cfix,
                aptrb,
                aptre,
                asub,
                aval,
                bkc,
                blc,
                buc,
                bkx,
                blx,
                bux)
        [aptrb : array(int64)]  Row or column start pointers.  
        [aptre : array(int64)]  Row or column end pointers.  
        [asub : array(int32)]  Coefficient subscripts.  
        [aval : array(float64)]  Coefficient values.  
        [bkc : array(mosek.boundkey)]  Bound keys for the constraints.  
        [bkx : array(mosek.boundkey)]  Bound keys for the variables.  
        [blc : array(float64)]  Lower bounds for the constraints.  
        [blx : array(float64)]  Lower bounds for the variables.  
        [buc : array(float64)]  Upper bounds for the constraints.  
        [bux : array(float64)]  Upper bounds for the variables.  
        [c : array(float64)]  Linear terms of the objective as a dense vector. The length is the number of variables.  
        [cfix : float64]  Fixed term in the objective.  
        [maxnumcon : int32]  Number of preallocated constraints in the optimization task.  
        [maxnumvar : int32]  Number of preallocated variables in the optimization task.  
      """
      return self.__inputdata64_iiOdOOOOOOOOOO_15(*args,**kwds)
    def __isdouparname_s_2(self,parname):
      _res_isdouparname,_retargs_isdouparname = self.__obj.isdouparname_s_2(parname)
      if _res_isdouparname != 0:
        _,_msg_isdouparname = self.__getlasterror(_res_isdouparname)
        raise Error(rescode(_res_isdouparname),_msg_isdouparname)
      else:
        (param) = _retargs_isdouparname
      return (dparam(param))
    def isdouparname(self,*args,**kwds):
      """
      Checks a double parameter name.
    
      isdouparname(parname) -> (param)
        [param : mosek.dparam]  Returns the parameter corresponding to the name, if one exists.  
        [parname : str]  Parameter name.  
      """
      return self.__isdouparname_s_2(*args,**kwds)
    def __isintparname_s_2(self,parname):
      _res_isintparname,_retargs_isintparname = self.__obj.isintparname_s_2(parname)
      if _res_isintparname != 0:
        _,_msg_isintparname = self.__getlasterror(_res_isintparname)
        raise Error(rescode(_res_isintparname),_msg_isintparname)
      else:
        (param) = _retargs_isintparname
      return (iparam(param))
    def isintparname(self,*args,**kwds):
      """
      Checks an integer parameter name.
    
      isintparname(parname) -> (param)
        [param : mosek.iparam]  Returns the parameter corresponding to the name, if one exists.  
        [parname : str]  Parameter name.  
      """
      return self.__isintparname_s_2(*args,**kwds)
    def __isstrparname_s_2(self,parname):
      _res_isstrparname,_retargs_isstrparname = self.__obj.isstrparname_s_2(parname)
      if _res_isstrparname != 0:
        _,_msg_isstrparname = self.__getlasterror(_res_isstrparname)
        raise Error(rescode(_res_isstrparname),_msg_isstrparname)
      else:
        (param) = _retargs_isstrparname
      return (sparam(param))
    def isstrparname(self,*args,**kwds):
      """
      Checks a string parameter name.
    
      isstrparname(parname) -> (param)
        [param : mosek.sparam]  Returns the parameter corresponding to the name, if one exists.  
        [parname : str]  Parameter name.  
      """
      return self.__isstrparname_s_2(*args,**kwds)
    def __linkfiletotaskstream_isi_4(self,whichstream,filename,append):
      _res_linkfiletotaskstream,_retargs_linkfiletotaskstream = self.__obj.linkfiletotaskstream_isi_4(whichstream,filename,append)
      if _res_linkfiletotaskstream != 0:
        _,_msg_linkfiletotaskstream = self.__getlasterror(_res_linkfiletotaskstream)
        raise Error(rescode(_res_linkfiletotaskstream),_msg_linkfiletotaskstream)
    def linkfiletostream(self,*args,**kwds):
      """
      Directs all output from a task stream to a file.
    
      linkfiletostream(whichstream,filename,append)
        [append : int32]  If this argument is 0 the output file will be overwritten, otherwise it will be appended to.  
        [filename : str]  A valid file name.  
        [whichstream : mosek.streamtype]  Index of the stream.  
      """
      return self.__linkfiletotaskstream_isi_4(*args,**kwds)
    def __primalrepair_OOOO_5(self,wlc,wuc,wlx,wux):
      copyback_wlc = False
      if wlc is None:
        wlc_ = None
        memview_wlc = None
      else:
        try:
          memview_wlc = memoryview(wlc)
        except TypeError:
          try:
            _tmparray_wlc = array.array("d",wlc)
          except TypeError:
            raise TypeError("Argument wlc has wrong type") from None
          else:
            memview_wlc = memoryview(_tmparray_wlc)
            copyback_wlc = True
            wlc_ = _tmparray_wlc
        else:
          if memview_wlc.ndim != 1:
            raise TypeError("Argument wlc must be one-dimensional")
          if memview_wlc.format != "d":
            _tmparray_wlc = array.array("d",wlc)
            memview_wlc = memoryview(_tmparray_wlc)
            copyback_wlc = True
            wlc_ = _tmparray_wlc
      copyback_wuc = False
      if wuc is None:
        wuc_ = None
        memview_wuc = None
      else:
        try:
          memview_wuc = memoryview(wuc)
        except TypeError:
          try:
            _tmparray_wuc = array.array("d",wuc)
          except TypeError:
            raise TypeError("Argument wuc has wrong type") from None
          else:
            memview_wuc = memoryview(_tmparray_wuc)
            copyback_wuc = True
            wuc_ = _tmparray_wuc
        else:
          if memview_wuc.ndim != 1:
            raise TypeError("Argument wuc must be one-dimensional")
          if memview_wuc.format != "d":
            _tmparray_wuc = array.array("d",wuc)
            memview_wuc = memoryview(_tmparray_wuc)
            copyback_wuc = True
            wuc_ = _tmparray_wuc
      copyback_wlx = False
      if wlx is None:
        wlx_ = None
        memview_wlx = None
      else:
        try:
          memview_wlx = memoryview(wlx)
        except TypeError:
          try:
            _tmparray_wlx = array.array("d",wlx)
          except TypeError:
            raise TypeError("Argument wlx has wrong type") from None
          else:
            memview_wlx = memoryview(_tmparray_wlx)
            copyback_wlx = True
            wlx_ = _tmparray_wlx
        else:
          if memview_wlx.ndim != 1:
            raise TypeError("Argument wlx must be one-dimensional")
          if memview_wlx.format != "d":
            _tmparray_wlx = array.array("d",wlx)
            memview_wlx = memoryview(_tmparray_wlx)
            copyback_wlx = True
            wlx_ = _tmparray_wlx
      copyback_wux = False
      if wux is None:
        wux_ = None
        memview_wux = None
      else:
        try:
          memview_wux = memoryview(wux)
        except TypeError:
          try:
            _tmparray_wux = array.array("d",wux)
          except TypeError:
            raise TypeError("Argument wux has wrong type") from None
          else:
            memview_wux = memoryview(_tmparray_wux)
            copyback_wux = True
            wux_ = _tmparray_wux
        else:
          if memview_wux.ndim != 1:
            raise TypeError("Argument wux must be one-dimensional")
          if memview_wux.format != "d":
            _tmparray_wux = array.array("d",wux)
            memview_wux = memoryview(_tmparray_wux)
            copyback_wux = True
            wux_ = _tmparray_wux
      _res_primalrepair,_retargs_primalrepair = self.__obj.primalrepair_OOOO_5(memview_wlc,memview_wuc,memview_wlx,memview_wux)
      if _res_primalrepair != 0:
        _,_msg_primalrepair = self.__getlasterror(_res_primalrepair)
        raise Error(rescode(_res_primalrepair),_msg_primalrepair)
    def primalrepair(self,*args,**kwds):
      """
      Repairs a primal infeasible optimization problem by adjusting the bounds on the constraints and variables.
    
      primalrepair(wlc,wuc,wlx,wux)
        [wlc : array(float64)]  Weights associated with relaxing lower bounds on the constraints.  
        [wlx : array(float64)]  Weights associated with relaxing the lower bounds of the variables.  
        [wuc : array(float64)]  Weights associated with relaxing the upper bound on the constraints.  
        [wux : array(float64)]  Weights associated with relaxing the upper bounds of variables.  
      """
      return self.__primalrepair_OOOO_5(*args,**kwds)
    def __infeasibilityreport_ii_3(self,whichstream,whichsol):
      _res_infeasibilityreport,_retargs_infeasibilityreport = self.__obj.infeasibilityreport_ii_3(whichstream,whichsol)
      if _res_infeasibilityreport != 0:
        _,_msg_infeasibilityreport = self.__getlasterror(_res_infeasibilityreport)
        raise Error(rescode(_res_infeasibilityreport),_msg_infeasibilityreport)
    def infeasibilityreport(self,*args,**kwds):
      """
      Prints the infeasibility report to an output stream.
    
      infeasibilityreport(whichstream,whichsol)
        [whichsol : mosek.soltype]  Selects a solution.  
        [whichstream : mosek.streamtype]  Index of the stream.  
      """
      return self.__infeasibilityreport_ii_3(*args,**kwds)
    def __toconic__1(self):
      _res_toconic,_retargs_toconic = self.__obj.toconic__1()
      if _res_toconic != 0:
        _,_msg_toconic = self.__getlasterror(_res_toconic)
        raise Error(rescode(_res_toconic),_msg_toconic)
    def toconic(self,*args,**kwds):
      """
      In-place reformulation of a QCQO to a conic quadratic problem.
    
      toconic()
      """
      return self.__toconic__1(*args,**kwds)
    def __optimizetrm__1(self):
      _res_optimizetrm,_retargs_optimizetrm = self.__obj.optimizetrm__1()
      if _res_optimizetrm != 0:
        _,_msg_optimizetrm = self.__getlasterror(_res_optimizetrm)
        raise Error(rescode(_res_optimizetrm),_msg_optimizetrm)
      else:
        (trmcode) = _retargs_optimizetrm
      return (rescode(trmcode))
    def optimize(self,*args,**kwds):
      """
      Optimizes the problem.
    
      optimize() -> (trmcode)
        [trmcode : mosek.rescode]  Is either OK or a termination response code.  
      """
      return self.__optimizetrm__1(*args,**kwds)
    def __commitchanges__1(self):
      _res_commitchanges,_retargs_commitchanges = self.__obj.commitchanges__1()
      if _res_commitchanges != 0:
        _,_msg_commitchanges = self.__getlasterror(_res_commitchanges)
        raise Error(rescode(_res_commitchanges),_msg_commitchanges)
    def commitchanges(self,*args,**kwds):
      """
      Commits all cached problem changes.
    
      commitchanges()
      """
      return self.__commitchanges__1(*args,**kwds)
    def __getatruncatetol_O_2(self,tolzero):
      if tolzero is None:
        raise TypeError("Argument tolzero may not be None")
      copyback_tolzero = False
      if tolzero is None:
        tolzero_ = None
        memview_tolzero = None
      else:
        try:
          memview_tolzero = memoryview(tolzero)
        except TypeError:
          try:
            _tmparray_tolzero = array.array("d",[0 for _ in range(len(tolzero))])
          except TypeError:
            raise TypeError("Argument tolzero has wrong type") from None
          else:
            memview_tolzero = memoryview(_tmparray_tolzero)
            copyback_tolzero = True
            tolzero_ = _tmparray_tolzero
        else:
          if memview_tolzero.ndim != 1:
            raise TypeError("Argument tolzero must be one-dimensional")
          if memview_tolzero.format != "d":
            _tmparray_tolzero = array.array("d",tolzero)
            memview_tolzero = memoryview(_tmparray_tolzero)
            copyback_tolzero = True
            tolzero_ = _tmparray_tolzero
      _res_getatruncatetol,_retargs_getatruncatetol = self.__obj.getatruncatetol_O_2(memview_tolzero)
      if _res_getatruncatetol != 0:
        _,_msg_getatruncatetol = self.__getlasterror(_res_getatruncatetol)
        raise Error(rescode(_res_getatruncatetol),_msg_getatruncatetol)
      if copyback_tolzero:
        for __tmp_820 in range(len(tolzero)): tolzero[__tmp_820] = tolzero_[__tmp_820]
    def __getatruncatetol_O_1(self):
      tolzero_ = bytearray(0)
      _res_getatruncatetol,_retargs_getatruncatetol = self.__obj.getatruncatetol_O_1(tolzero_)
      if _res_getatruncatetol != 0:
        _,_msg_getatruncatetol = self.__getlasterror(_res_getatruncatetol)
        raise Error(rescode(_res_getatruncatetol),_msg_getatruncatetol)
      tolzero = array.array("d")
      tolzero.frombytes(tolzero_)
      return (tolzero)
    def getatruncatetol(self,*args,**kwds):
      """
      Gets the current A matrix truncation threshold.
    
      getatruncatetol(tolzero)
      getatruncatetol() -> (tolzero)
        [tolzero : array(float64)]  Truncation tolerance.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 2: return self.__getatruncatetol_O_2(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getatruncatetol_O_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __putatruncatetol_d_2(self,tolzero):
      _res_putatruncatetol,_retargs_putatruncatetol = self.__obj.putatruncatetol_d_2(tolzero)
      if _res_putatruncatetol != 0:
        _,_msg_putatruncatetol = self.__getlasterror(_res_putatruncatetol)
        raise Error(rescode(_res_putatruncatetol),_msg_putatruncatetol)
    def putatruncatetol(self,*args,**kwds):
      """
      Truncates all elements in A below a certain tolerance to zero.
    
      putatruncatetol(tolzero)
        [tolzero : float64]  Truncation tolerance.  
      """
      return self.__putatruncatetol_d_2(*args,**kwds)
    def __putaij_iid_4(self,i,j,aij):
      _res_putaij,_retargs_putaij = self.__obj.putaij_iid_4(i,j,aij)
      if _res_putaij != 0:
        _,_msg_putaij = self.__getlasterror(_res_putaij)
        raise Error(rescode(_res_putaij),_msg_putaij)
    def putaij(self,*args,**kwds):
      """
      Changes a single value in the linear coefficient matrix.
    
      putaij(i,j,aij)
        [aij : float64]  New coefficient.  
        [i : int32]  Constraint (row) index.  
        [j : int32]  Variable (column) index.  
      """
      return self.__putaij_iid_4(*args,**kwds)
    def __putaijlist64_OOO_4(self,subi,subj,valij):
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",subi)
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if valij is None:
        raise TypeError("Argument valij may not be None")
      copyback_valij = False
      if valij is None:
        valij_ = None
        memview_valij = None
      else:
        try:
          memview_valij = memoryview(valij)
        except TypeError:
          try:
            _tmparray_valij = array.array("d",valij)
          except TypeError:
            raise TypeError("Argument valij has wrong type") from None
          else:
            memview_valij = memoryview(_tmparray_valij)
            copyback_valij = True
            valij_ = _tmparray_valij
        else:
          if memview_valij.ndim != 1:
            raise TypeError("Argument valij must be one-dimensional")
          if memview_valij.format != "d":
            _tmparray_valij = array.array("d",valij)
            memview_valij = memoryview(_tmparray_valij)
            copyback_valij = True
            valij_ = _tmparray_valij
      _res_putaijlist64,_retargs_putaijlist64 = self.__obj.putaijlist64_OOO_4(memview_subi,memview_subj,memview_valij)
      if _res_putaijlist64 != 0:
        _,_msg_putaijlist64 = self.__getlasterror(_res_putaijlist64)
        raise Error(rescode(_res_putaijlist64),_msg_putaijlist64)
    def putaijlist(self,*args,**kwds):
      """
      Changes one or more coefficients in the linear constraint matrix.
    
      putaijlist(subi,subj,valij)
        [subi : array(int32)]  Constraint (row) indices.  
        [subj : array(int32)]  Variable (column) indices.  
        [valij : array(float64)]  New coefficient values.  
      """
      return self.__putaijlist64_OOO_4(*args,**kwds)
    def __putacol_iOO_4(self,j,subj,valj):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if valj is None:
        raise TypeError("Argument valj may not be None")
      copyback_valj = False
      if valj is None:
        valj_ = None
        memview_valj = None
      else:
        try:
          memview_valj = memoryview(valj)
        except TypeError:
          try:
            _tmparray_valj = array.array("d",valj)
          except TypeError:
            raise TypeError("Argument valj has wrong type") from None
          else:
            memview_valj = memoryview(_tmparray_valj)
            copyback_valj = True
            valj_ = _tmparray_valj
        else:
          if memview_valj.ndim != 1:
            raise TypeError("Argument valj must be one-dimensional")
          if memview_valj.format != "d":
            _tmparray_valj = array.array("d",valj)
            memview_valj = memoryview(_tmparray_valj)
            copyback_valj = True
            valj_ = _tmparray_valj
      _res_putacol,_retargs_putacol = self.__obj.putacol_iOO_4(j,memview_subj,memview_valj)
      if _res_putacol != 0:
        _,_msg_putacol = self.__getlasterror(_res_putacol)
        raise Error(rescode(_res_putacol),_msg_putacol)
    def putacol(self,*args,**kwds):
      """
      Replaces all elements in one column of the linear constraint matrix.
    
      putacol(j,subj,valj)
        [j : int32]  Column index.  
        [subj : array(int32)]  Row indexes of non-zero values in column.  
        [valj : array(float64)]  New non-zero values of column.  
      """
      return self.__putacol_iOO_4(*args,**kwds)
    def __putarow_iOO_4(self,i,subi,vali):
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",subi)
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if vali is None:
        raise TypeError("Argument vali may not be None")
      copyback_vali = False
      if vali is None:
        vali_ = None
        memview_vali = None
      else:
        try:
          memview_vali = memoryview(vali)
        except TypeError:
          try:
            _tmparray_vali = array.array("d",vali)
          except TypeError:
            raise TypeError("Argument vali has wrong type") from None
          else:
            memview_vali = memoryview(_tmparray_vali)
            copyback_vali = True
            vali_ = _tmparray_vali
        else:
          if memview_vali.ndim != 1:
            raise TypeError("Argument vali must be one-dimensional")
          if memview_vali.format != "d":
            _tmparray_vali = array.array("d",vali)
            memview_vali = memoryview(_tmparray_vali)
            copyback_vali = True
            vali_ = _tmparray_vali
      _res_putarow,_retargs_putarow = self.__obj.putarow_iOO_4(i,memview_subi,memview_vali)
      if _res_putarow != 0:
        _,_msg_putarow = self.__getlasterror(_res_putarow)
        raise Error(rescode(_res_putarow),_msg_putarow)
    def putarow(self,*args,**kwds):
      """
      Replaces all elements in one row of the linear constraint matrix.
    
      putarow(i,subi,vali)
        [i : int32]  Row index.  
        [subi : array(int32)]  Column indexes of non-zero values in row.  
        [vali : array(float64)]  New non-zero values of row.  
      """
      return self.__putarow_iOO_4(*args,**kwds)
    def __putarowslice64_iiOOOO_7(self,first,last,ptrb,ptre,asub,aval):
      if ptrb is None:
        raise TypeError("Argument ptrb may not be None")
      copyback_ptrb = False
      if ptrb is None:
        ptrb_ = None
        memview_ptrb = None
      else:
        try:
          memview_ptrb = memoryview(ptrb)
        except TypeError:
          try:
            _tmparray_ptrb = array.array("q",ptrb)
          except TypeError:
            raise TypeError("Argument ptrb has wrong type") from None
          else:
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
        else:
          if memview_ptrb.ndim != 1:
            raise TypeError("Argument ptrb must be one-dimensional")
          if memview_ptrb.format != "q":
            _tmparray_ptrb = array.array("q",ptrb)
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
      if ptre is None:
        raise TypeError("Argument ptre may not be None")
      copyback_ptre = False
      if ptre is None:
        ptre_ = None
        memview_ptre = None
      else:
        try:
          memview_ptre = memoryview(ptre)
        except TypeError:
          try:
            _tmparray_ptre = array.array("q",ptre)
          except TypeError:
            raise TypeError("Argument ptre has wrong type") from None
          else:
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
        else:
          if memview_ptre.ndim != 1:
            raise TypeError("Argument ptre must be one-dimensional")
          if memview_ptre.format != "q":
            _tmparray_ptre = array.array("q",ptre)
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
      if asub is None:
        raise TypeError("Argument asub may not be None")
      copyback_asub = False
      if asub is None:
        asub_ = None
        memview_asub = None
      else:
        try:
          memview_asub = memoryview(asub)
        except TypeError:
          try:
            _tmparray_asub = array.array("i",asub)
          except TypeError:
            raise TypeError("Argument asub has wrong type") from None
          else:
            memview_asub = memoryview(_tmparray_asub)
            copyback_asub = True
            asub_ = _tmparray_asub
        else:
          if memview_asub.ndim != 1:
            raise TypeError("Argument asub must be one-dimensional")
          if memview_asub.format != "i":
            _tmparray_asub = array.array("i",asub)
            memview_asub = memoryview(_tmparray_asub)
            copyback_asub = True
            asub_ = _tmparray_asub
      if aval is None:
        raise TypeError("Argument aval may not be None")
      copyback_aval = False
      if aval is None:
        aval_ = None
        memview_aval = None
      else:
        try:
          memview_aval = memoryview(aval)
        except TypeError:
          try:
            _tmparray_aval = array.array("d",aval)
          except TypeError:
            raise TypeError("Argument aval has wrong type") from None
          else:
            memview_aval = memoryview(_tmparray_aval)
            copyback_aval = True
            aval_ = _tmparray_aval
        else:
          if memview_aval.ndim != 1:
            raise TypeError("Argument aval must be one-dimensional")
          if memview_aval.format != "d":
            _tmparray_aval = array.array("d",aval)
            memview_aval = memoryview(_tmparray_aval)
            copyback_aval = True
            aval_ = _tmparray_aval
      _res_putarowslice64,_retargs_putarowslice64 = self.__obj.putarowslice64_iiOOOO_7(first,last,memview_ptrb,memview_ptre,memview_asub,memview_aval)
      if _res_putarowslice64 != 0:
        _,_msg_putarowslice64 = self.__getlasterror(_res_putarowslice64)
        raise Error(rescode(_res_putarowslice64),_msg_putarowslice64)
    def putarowslice(self,*args,**kwds):
      """
      Replaces all elements in several rows the linear constraint matrix.
    
      putarowslice(first,last,ptrb,ptre,asub,aval)
        [asub : array(int32)]  Column indexes of new elements.  
        [aval : array(float64)]  Coefficient values.  
        [first : int32]  First row in the slice.  
        [last : int32]  Last row plus one in the slice.  
        [ptrb : array(int64)]  Array of pointers to the first element in the rows.  
        [ptre : array(int64)]  Array of pointers to the last element plus one in the rows.  
      """
      return self.__putarowslice64_iiOOOO_7(*args,**kwds)
    def __putarowlist64_OOOOO_6(self,sub,ptrb,ptre,asub,aval):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if ptrb is None:
        raise TypeError("Argument ptrb may not be None")
      copyback_ptrb = False
      if ptrb is None:
        ptrb_ = None
        memview_ptrb = None
      else:
        try:
          memview_ptrb = memoryview(ptrb)
        except TypeError:
          try:
            _tmparray_ptrb = array.array("q",ptrb)
          except TypeError:
            raise TypeError("Argument ptrb has wrong type") from None
          else:
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
        else:
          if memview_ptrb.ndim != 1:
            raise TypeError("Argument ptrb must be one-dimensional")
          if memview_ptrb.format != "q":
            _tmparray_ptrb = array.array("q",ptrb)
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
      if ptre is None:
        raise TypeError("Argument ptre may not be None")
      copyback_ptre = False
      if ptre is None:
        ptre_ = None
        memview_ptre = None
      else:
        try:
          memview_ptre = memoryview(ptre)
        except TypeError:
          try:
            _tmparray_ptre = array.array("q",ptre)
          except TypeError:
            raise TypeError("Argument ptre has wrong type") from None
          else:
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
        else:
          if memview_ptre.ndim != 1:
            raise TypeError("Argument ptre must be one-dimensional")
          if memview_ptre.format != "q":
            _tmparray_ptre = array.array("q",ptre)
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
      if asub is None:
        raise TypeError("Argument asub may not be None")
      copyback_asub = False
      if asub is None:
        asub_ = None
        memview_asub = None
      else:
        try:
          memview_asub = memoryview(asub)
        except TypeError:
          try:
            _tmparray_asub = array.array("i",asub)
          except TypeError:
            raise TypeError("Argument asub has wrong type") from None
          else:
            memview_asub = memoryview(_tmparray_asub)
            copyback_asub = True
            asub_ = _tmparray_asub
        else:
          if memview_asub.ndim != 1:
            raise TypeError("Argument asub must be one-dimensional")
          if memview_asub.format != "i":
            _tmparray_asub = array.array("i",asub)
            memview_asub = memoryview(_tmparray_asub)
            copyback_asub = True
            asub_ = _tmparray_asub
      if aval is None:
        raise TypeError("Argument aval may not be None")
      copyback_aval = False
      if aval is None:
        aval_ = None
        memview_aval = None
      else:
        try:
          memview_aval = memoryview(aval)
        except TypeError:
          try:
            _tmparray_aval = array.array("d",aval)
          except TypeError:
            raise TypeError("Argument aval has wrong type") from None
          else:
            memview_aval = memoryview(_tmparray_aval)
            copyback_aval = True
            aval_ = _tmparray_aval
        else:
          if memview_aval.ndim != 1:
            raise TypeError("Argument aval must be one-dimensional")
          if memview_aval.format != "d":
            _tmparray_aval = array.array("d",aval)
            memview_aval = memoryview(_tmparray_aval)
            copyback_aval = True
            aval_ = _tmparray_aval
      _res_putarowlist64,_retargs_putarowlist64 = self.__obj.putarowlist64_OOOOO_6(memview_sub,memview_ptrb,memview_ptre,memview_asub,memview_aval)
      if _res_putarowlist64 != 0:
        _,_msg_putarowlist64 = self.__getlasterror(_res_putarowlist64)
        raise Error(rescode(_res_putarowlist64),_msg_putarowlist64)
    def putarowlist(self,*args,**kwds):
      """
      Replaces all elements in several rows of the linear constraint matrix.
    
      putarowlist(sub,ptrb,ptre,asub,aval)
        [asub : array(int32)]  Variable indexes.  
        [aval : array(float64)]  Coefficient values.  
        [ptrb : array(int64)]  Array of pointers to the first element in the rows.  
        [ptre : array(int64)]  Array of pointers to the last element plus one in the rows.  
        [sub : array(int32)]  Indexes of rows or columns that should be replaced.  
      """
      return self.__putarowlist64_OOOOO_6(*args,**kwds)
    def __putacolslice64_iiOOOO_7(self,first,last,ptrb,ptre,asub,aval):
      if ptrb is None:
        raise TypeError("Argument ptrb may not be None")
      copyback_ptrb = False
      if ptrb is None:
        ptrb_ = None
        memview_ptrb = None
      else:
        try:
          memview_ptrb = memoryview(ptrb)
        except TypeError:
          try:
            _tmparray_ptrb = array.array("q",ptrb)
          except TypeError:
            raise TypeError("Argument ptrb has wrong type") from None
          else:
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
        else:
          if memview_ptrb.ndim != 1:
            raise TypeError("Argument ptrb must be one-dimensional")
          if memview_ptrb.format != "q":
            _tmparray_ptrb = array.array("q",ptrb)
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
      if ptre is None:
        raise TypeError("Argument ptre may not be None")
      copyback_ptre = False
      if ptre is None:
        ptre_ = None
        memview_ptre = None
      else:
        try:
          memview_ptre = memoryview(ptre)
        except TypeError:
          try:
            _tmparray_ptre = array.array("q",ptre)
          except TypeError:
            raise TypeError("Argument ptre has wrong type") from None
          else:
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
        else:
          if memview_ptre.ndim != 1:
            raise TypeError("Argument ptre must be one-dimensional")
          if memview_ptre.format != "q":
            _tmparray_ptre = array.array("q",ptre)
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
      if asub is None:
        raise TypeError("Argument asub may not be None")
      copyback_asub = False
      if asub is None:
        asub_ = None
        memview_asub = None
      else:
        try:
          memview_asub = memoryview(asub)
        except TypeError:
          try:
            _tmparray_asub = array.array("i",asub)
          except TypeError:
            raise TypeError("Argument asub has wrong type") from None
          else:
            memview_asub = memoryview(_tmparray_asub)
            copyback_asub = True
            asub_ = _tmparray_asub
        else:
          if memview_asub.ndim != 1:
            raise TypeError("Argument asub must be one-dimensional")
          if memview_asub.format != "i":
            _tmparray_asub = array.array("i",asub)
            memview_asub = memoryview(_tmparray_asub)
            copyback_asub = True
            asub_ = _tmparray_asub
      if aval is None:
        raise TypeError("Argument aval may not be None")
      copyback_aval = False
      if aval is None:
        aval_ = None
        memview_aval = None
      else:
        try:
          memview_aval = memoryview(aval)
        except TypeError:
          try:
            _tmparray_aval = array.array("d",aval)
          except TypeError:
            raise TypeError("Argument aval has wrong type") from None
          else:
            memview_aval = memoryview(_tmparray_aval)
            copyback_aval = True
            aval_ = _tmparray_aval
        else:
          if memview_aval.ndim != 1:
            raise TypeError("Argument aval must be one-dimensional")
          if memview_aval.format != "d":
            _tmparray_aval = array.array("d",aval)
            memview_aval = memoryview(_tmparray_aval)
            copyback_aval = True
            aval_ = _tmparray_aval
      _res_putacolslice64,_retargs_putacolslice64 = self.__obj.putacolslice64_iiOOOO_7(first,last,memview_ptrb,memview_ptre,memview_asub,memview_aval)
      if _res_putacolslice64 != 0:
        _,_msg_putacolslice64 = self.__getlasterror(_res_putacolslice64)
        raise Error(rescode(_res_putacolslice64),_msg_putacolslice64)
    def putacolslice(self,*args,**kwds):
      """
      Replaces all elements in a sequence of columns the linear constraint matrix.
    
      putacolslice(first,last,ptrb,ptre,asub,aval)
        [asub : array(int32)]  Row indexes  
        [aval : array(float64)]  Coefficient values.  
        [first : int32]  First column in the slice.  
        [last : int32]  Last column plus one in the slice.  
        [ptrb : array(int64)]  Array of pointers to the first element in the columns.  
        [ptre : array(int64)]  Array of pointers to the last element plus one in the columns.  
      """
      return self.__putacolslice64_iiOOOO_7(*args,**kwds)
    def __putacollist64_OOOOO_6(self,sub,ptrb,ptre,asub,aval):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if ptrb is None:
        raise TypeError("Argument ptrb may not be None")
      copyback_ptrb = False
      if ptrb is None:
        ptrb_ = None
        memview_ptrb = None
      else:
        try:
          memview_ptrb = memoryview(ptrb)
        except TypeError:
          try:
            _tmparray_ptrb = array.array("q",ptrb)
          except TypeError:
            raise TypeError("Argument ptrb has wrong type") from None
          else:
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
        else:
          if memview_ptrb.ndim != 1:
            raise TypeError("Argument ptrb must be one-dimensional")
          if memview_ptrb.format != "q":
            _tmparray_ptrb = array.array("q",ptrb)
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
      if ptre is None:
        raise TypeError("Argument ptre may not be None")
      copyback_ptre = False
      if ptre is None:
        ptre_ = None
        memview_ptre = None
      else:
        try:
          memview_ptre = memoryview(ptre)
        except TypeError:
          try:
            _tmparray_ptre = array.array("q",ptre)
          except TypeError:
            raise TypeError("Argument ptre has wrong type") from None
          else:
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
        else:
          if memview_ptre.ndim != 1:
            raise TypeError("Argument ptre must be one-dimensional")
          if memview_ptre.format != "q":
            _tmparray_ptre = array.array("q",ptre)
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
      if asub is None:
        raise TypeError("Argument asub may not be None")
      copyback_asub = False
      if asub is None:
        asub_ = None
        memview_asub = None
      else:
        try:
          memview_asub = memoryview(asub)
        except TypeError:
          try:
            _tmparray_asub = array.array("i",asub)
          except TypeError:
            raise TypeError("Argument asub has wrong type") from None
          else:
            memview_asub = memoryview(_tmparray_asub)
            copyback_asub = True
            asub_ = _tmparray_asub
        else:
          if memview_asub.ndim != 1:
            raise TypeError("Argument asub must be one-dimensional")
          if memview_asub.format != "i":
            _tmparray_asub = array.array("i",asub)
            memview_asub = memoryview(_tmparray_asub)
            copyback_asub = True
            asub_ = _tmparray_asub
      if aval is None:
        raise TypeError("Argument aval may not be None")
      copyback_aval = False
      if aval is None:
        aval_ = None
        memview_aval = None
      else:
        try:
          memview_aval = memoryview(aval)
        except TypeError:
          try:
            _tmparray_aval = array.array("d",aval)
          except TypeError:
            raise TypeError("Argument aval has wrong type") from None
          else:
            memview_aval = memoryview(_tmparray_aval)
            copyback_aval = True
            aval_ = _tmparray_aval
        else:
          if memview_aval.ndim != 1:
            raise TypeError("Argument aval must be one-dimensional")
          if memview_aval.format != "d":
            _tmparray_aval = array.array("d",aval)
            memview_aval = memoryview(_tmparray_aval)
            copyback_aval = True
            aval_ = _tmparray_aval
      _res_putacollist64,_retargs_putacollist64 = self.__obj.putacollist64_OOOOO_6(memview_sub,memview_ptrb,memview_ptre,memview_asub,memview_aval)
      if _res_putacollist64 != 0:
        _,_msg_putacollist64 = self.__getlasterror(_res_putacollist64)
        raise Error(rescode(_res_putacollist64),_msg_putacollist64)
    def putacollist(self,*args,**kwds):
      """
      Replaces all elements in several columns the linear constraint matrix.
    
      putacollist(sub,ptrb,ptre,asub,aval)
        [asub : array(int32)]  Row indexes  
        [aval : array(float64)]  Coefficient values.  
        [ptrb : array(int64)]  Array of pointers to the first element in the columns.  
        [ptre : array(int64)]  Array of pointers to the last element plus one in the columns.  
        [sub : array(int32)]  Indexes of columns that should be replaced.  
      """
      return self.__putacollist64_OOOOO_6(*args,**kwds)
    def __putbaraij_iiOO_5(self,i,j,sub,weights):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("q",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "q":
            _tmparray_sub = array.array("q",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if weights is None:
        raise TypeError("Argument weights may not be None")
      copyback_weights = False
      if weights is None:
        weights_ = None
        memview_weights = None
      else:
        try:
          memview_weights = memoryview(weights)
        except TypeError:
          try:
            _tmparray_weights = array.array("d",weights)
          except TypeError:
            raise TypeError("Argument weights has wrong type") from None
          else:
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
        else:
          if memview_weights.ndim != 1:
            raise TypeError("Argument weights must be one-dimensional")
          if memview_weights.format != "d":
            _tmparray_weights = array.array("d",weights)
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
      _res_putbaraij,_retargs_putbaraij = self.__obj.putbaraij_iiOO_5(i,j,memview_sub,memview_weights)
      if _res_putbaraij != 0:
        _,_msg_putbaraij = self.__getlasterror(_res_putbaraij)
        raise Error(rescode(_res_putbaraij),_msg_putbaraij)
    def putbaraij(self,*args,**kwds):
      """
      Inputs an element of barA.
    
      putbaraij(i,j,sub,weights)
        [i : int32]  Row index of barA.  
        [j : int32]  Column index of barA.  
        [sub : array(int64)]  Element indexes in matrix storage.  
        [weights : array(float64)]  Weights in the weighted sum.  
      """
      return self.__putbaraij_iiOO_5(*args,**kwds)
    def __putbaraijlist_OOOOOO_7(self,subi,subj,alphaptrb,alphaptre,matidx,weights):
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",subi)
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if alphaptrb is None:
        raise TypeError("Argument alphaptrb may not be None")
      copyback_alphaptrb = False
      if alphaptrb is None:
        alphaptrb_ = None
        memview_alphaptrb = None
      else:
        try:
          memview_alphaptrb = memoryview(alphaptrb)
        except TypeError:
          try:
            _tmparray_alphaptrb = array.array("q",alphaptrb)
          except TypeError:
            raise TypeError("Argument alphaptrb has wrong type") from None
          else:
            memview_alphaptrb = memoryview(_tmparray_alphaptrb)
            copyback_alphaptrb = True
            alphaptrb_ = _tmparray_alphaptrb
        else:
          if memview_alphaptrb.ndim != 1:
            raise TypeError("Argument alphaptrb must be one-dimensional")
          if memview_alphaptrb.format != "q":
            _tmparray_alphaptrb = array.array("q",alphaptrb)
            memview_alphaptrb = memoryview(_tmparray_alphaptrb)
            copyback_alphaptrb = True
            alphaptrb_ = _tmparray_alphaptrb
      if alphaptre is None:
        raise TypeError("Argument alphaptre may not be None")
      copyback_alphaptre = False
      if alphaptre is None:
        alphaptre_ = None
        memview_alphaptre = None
      else:
        try:
          memview_alphaptre = memoryview(alphaptre)
        except TypeError:
          try:
            _tmparray_alphaptre = array.array("q",alphaptre)
          except TypeError:
            raise TypeError("Argument alphaptre has wrong type") from None
          else:
            memview_alphaptre = memoryview(_tmparray_alphaptre)
            copyback_alphaptre = True
            alphaptre_ = _tmparray_alphaptre
        else:
          if memview_alphaptre.ndim != 1:
            raise TypeError("Argument alphaptre must be one-dimensional")
          if memview_alphaptre.format != "q":
            _tmparray_alphaptre = array.array("q",alphaptre)
            memview_alphaptre = memoryview(_tmparray_alphaptre)
            copyback_alphaptre = True
            alphaptre_ = _tmparray_alphaptre
      if matidx is None:
        raise TypeError("Argument matidx may not be None")
      copyback_matidx = False
      if matidx is None:
        matidx_ = None
        memview_matidx = None
      else:
        try:
          memview_matidx = memoryview(matidx)
        except TypeError:
          try:
            _tmparray_matidx = array.array("q",matidx)
          except TypeError:
            raise TypeError("Argument matidx has wrong type") from None
          else:
            memview_matidx = memoryview(_tmparray_matidx)
            copyback_matidx = True
            matidx_ = _tmparray_matidx
        else:
          if memview_matidx.ndim != 1:
            raise TypeError("Argument matidx must be one-dimensional")
          if memview_matidx.format != "q":
            _tmparray_matidx = array.array("q",matidx)
            memview_matidx = memoryview(_tmparray_matidx)
            copyback_matidx = True
            matidx_ = _tmparray_matidx
      if weights is None:
        raise TypeError("Argument weights may not be None")
      copyback_weights = False
      if weights is None:
        weights_ = None
        memview_weights = None
      else:
        try:
          memview_weights = memoryview(weights)
        except TypeError:
          try:
            _tmparray_weights = array.array("d",weights)
          except TypeError:
            raise TypeError("Argument weights has wrong type") from None
          else:
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
        else:
          if memview_weights.ndim != 1:
            raise TypeError("Argument weights must be one-dimensional")
          if memview_weights.format != "d":
            _tmparray_weights = array.array("d",weights)
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
      _res_putbaraijlist,_retargs_putbaraijlist = self.__obj.putbaraijlist_OOOOOO_7(memview_subi,memview_subj,memview_alphaptrb,memview_alphaptre,memview_matidx,memview_weights)
      if _res_putbaraijlist != 0:
        _,_msg_putbaraijlist = self.__getlasterror(_res_putbaraijlist)
        raise Error(rescode(_res_putbaraijlist),_msg_putbaraijlist)
    def putbaraijlist(self,*args,**kwds):
      """
      Inputs list of elements of barA.
    
      putbaraijlist(subi,
                    subj,
                    alphaptrb,
                    alphaptre,
                    matidx,
                    weights)
        [alphaptrb : array(int64)]  Start entries for terms in the weighted sum.  
        [alphaptre : array(int64)]  End entries for terms in the weighted sum.  
        [matidx : array(int64)]  Element indexes in matrix storage.  
        [subi : array(int32)]  Row index of barA.  
        [subj : array(int32)]  Column index of barA.  
        [weights : array(float64)]  Weights in the weighted sum.  
      """
      return self.__putbaraijlist_OOOOOO_7(*args,**kwds)
    def __putbararowlist_OOOOOOO_8(self,subi,ptrb,ptre,subj,nummat,matidx,weights):
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",subi)
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if ptrb is None:
        raise TypeError("Argument ptrb may not be None")
      copyback_ptrb = False
      if ptrb is None:
        ptrb_ = None
        memview_ptrb = None
      else:
        try:
          memview_ptrb = memoryview(ptrb)
        except TypeError:
          try:
            _tmparray_ptrb = array.array("q",ptrb)
          except TypeError:
            raise TypeError("Argument ptrb has wrong type") from None
          else:
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
        else:
          if memview_ptrb.ndim != 1:
            raise TypeError("Argument ptrb must be one-dimensional")
          if memview_ptrb.format != "q":
            _tmparray_ptrb = array.array("q",ptrb)
            memview_ptrb = memoryview(_tmparray_ptrb)
            copyback_ptrb = True
            ptrb_ = _tmparray_ptrb
      if ptre is None:
        raise TypeError("Argument ptre may not be None")
      copyback_ptre = False
      if ptre is None:
        ptre_ = None
        memview_ptre = None
      else:
        try:
          memview_ptre = memoryview(ptre)
        except TypeError:
          try:
            _tmparray_ptre = array.array("q",ptre)
          except TypeError:
            raise TypeError("Argument ptre has wrong type") from None
          else:
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
        else:
          if memview_ptre.ndim != 1:
            raise TypeError("Argument ptre must be one-dimensional")
          if memview_ptre.format != "q":
            _tmparray_ptre = array.array("q",ptre)
            memview_ptre = memoryview(_tmparray_ptre)
            copyback_ptre = True
            ptre_ = _tmparray_ptre
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if nummat is None:
        raise TypeError("Argument nummat may not be None")
      copyback_nummat = False
      if nummat is None:
        nummat_ = None
        memview_nummat = None
      else:
        try:
          memview_nummat = memoryview(nummat)
        except TypeError:
          try:
            _tmparray_nummat = array.array("q",nummat)
          except TypeError:
            raise TypeError("Argument nummat has wrong type") from None
          else:
            memview_nummat = memoryview(_tmparray_nummat)
            copyback_nummat = True
            nummat_ = _tmparray_nummat
        else:
          if memview_nummat.ndim != 1:
            raise TypeError("Argument nummat must be one-dimensional")
          if memview_nummat.format != "q":
            _tmparray_nummat = array.array("q",nummat)
            memview_nummat = memoryview(_tmparray_nummat)
            copyback_nummat = True
            nummat_ = _tmparray_nummat
      if matidx is None:
        raise TypeError("Argument matidx may not be None")
      copyback_matidx = False
      if matidx is None:
        matidx_ = None
        memview_matidx = None
      else:
        try:
          memview_matidx = memoryview(matidx)
        except TypeError:
          try:
            _tmparray_matidx = array.array("q",matidx)
          except TypeError:
            raise TypeError("Argument matidx has wrong type") from None
          else:
            memview_matidx = memoryview(_tmparray_matidx)
            copyback_matidx = True
            matidx_ = _tmparray_matidx
        else:
          if memview_matidx.ndim != 1:
            raise TypeError("Argument matidx must be one-dimensional")
          if memview_matidx.format != "q":
            _tmparray_matidx = array.array("q",matidx)
            memview_matidx = memoryview(_tmparray_matidx)
            copyback_matidx = True
            matidx_ = _tmparray_matidx
      if weights is None:
        raise TypeError("Argument weights may not be None")
      copyback_weights = False
      if weights is None:
        weights_ = None
        memview_weights = None
      else:
        try:
          memview_weights = memoryview(weights)
        except TypeError:
          try:
            _tmparray_weights = array.array("d",weights)
          except TypeError:
            raise TypeError("Argument weights has wrong type") from None
          else:
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
        else:
          if memview_weights.ndim != 1:
            raise TypeError("Argument weights must be one-dimensional")
          if memview_weights.format != "d":
            _tmparray_weights = array.array("d",weights)
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
      _res_putbararowlist,_retargs_putbararowlist = self.__obj.putbararowlist_OOOOOOO_8(memview_subi,memview_ptrb,memview_ptre,memview_subj,memview_nummat,memview_matidx,memview_weights)
      if _res_putbararowlist != 0:
        _,_msg_putbararowlist = self.__getlasterror(_res_putbararowlist)
        raise Error(rescode(_res_putbararowlist),_msg_putbararowlist)
    def putbararowlist(self,*args,**kwds):
      """
      Replace a set of rows of barA
    
      putbararowlist(subi,
                     ptrb,
                     ptre,
                     subj,
                     nummat,
                     matidx,
                     weights)
        [matidx : array(int64)]  Matrix indexes for weighted sum of matrixes.  
        [nummat : array(int64)]  Number of entries in weighted sum of matrixes.  
        [ptrb : array(int64)]  Start of rows in barA.  
        [ptre : array(int64)]  End of rows in barA.  
        [subi : array(int32)]  Row indexes of barA.  
        [subj : array(int32)]  Column index of barA.  
        [weights : array(float64)]  Weights for weighted sum of matrixes.  
      """
      return self.__putbararowlist_OOOOOOO_8(*args,**kwds)
    def __getnumbarcnz__1(self):
      _res_getnumbarcnz,_retargs_getnumbarcnz = self.__obj.getnumbarcnz__1()
      if _res_getnumbarcnz != 0:
        _,_msg_getnumbarcnz = self.__getlasterror(_res_getnumbarcnz)
        raise Error(rescode(_res_getnumbarcnz),_msg_getnumbarcnz)
      else:
        (nz) = _retargs_getnumbarcnz
      return (nz)
    def getnumbarcnz(self,*args,**kwds):
      """
      Obtains the number of nonzero elements in barc.
    
      getnumbarcnz() -> (nz)
        [nz : int64]  The number of nonzero elements in barc.  
      """
      return self.__getnumbarcnz__1(*args,**kwds)
    def __getnumbaranz__1(self):
      _res_getnumbaranz,_retargs_getnumbaranz = self.__obj.getnumbaranz__1()
      if _res_getnumbaranz != 0:
        _,_msg_getnumbaranz = self.__getlasterror(_res_getnumbaranz)
        raise Error(rescode(_res_getnumbaranz),_msg_getnumbaranz)
      else:
        (nz) = _retargs_getnumbaranz
      return (nz)
    def getnumbaranz(self,*args,**kwds):
      """
      Get the number of nonzero elements in barA.
    
      getnumbaranz() -> (nz)
        [nz : int64]  The number of nonzero block elements in barA.  
      """
      return self.__getnumbaranz__1(*args,**kwds)
    def __getbarcsparsity_O_2(self,idxj):
      if idxj is None:
        raise TypeError("Argument idxj may not be None")
      copyback_idxj = False
      if idxj is None:
        idxj_ = None
        memview_idxj = None
      else:
        try:
          memview_idxj = memoryview(idxj)
        except TypeError:
          try:
            _tmparray_idxj = array.array("q",[0 for _ in range(len(idxj))])
          except TypeError:
            raise TypeError("Argument idxj has wrong type") from None
          else:
            memview_idxj = memoryview(_tmparray_idxj)
            copyback_idxj = True
            idxj_ = _tmparray_idxj
        else:
          if memview_idxj.ndim != 1:
            raise TypeError("Argument idxj must be one-dimensional")
          if memview_idxj.format != "q":
            _tmparray_idxj = array.array("q",idxj)
            memview_idxj = memoryview(_tmparray_idxj)
            copyback_idxj = True
            idxj_ = _tmparray_idxj
      _res_getbarcsparsity,_retargs_getbarcsparsity = self.__obj.getbarcsparsity_O_2(memview_idxj)
      if _res_getbarcsparsity != 0:
        _,_msg_getbarcsparsity = self.__getlasterror(_res_getbarcsparsity)
        raise Error(rescode(_res_getbarcsparsity),_msg_getbarcsparsity)
      else:
        (numnz) = _retargs_getbarcsparsity
      if copyback_idxj:
        for __tmp_920 in range(len(idxj)): idxj[__tmp_920] = idxj_[__tmp_920]
      return (numnz)
    def __getbarcsparsity_O_1(self):
      idxj_ = bytearray(0)
      _res_getbarcsparsity,_retargs_getbarcsparsity = self.__obj.getbarcsparsity_O_1(idxj_)
      if _res_getbarcsparsity != 0:
        _,_msg_getbarcsparsity = self.__getlasterror(_res_getbarcsparsity)
        raise Error(rescode(_res_getbarcsparsity),_msg_getbarcsparsity)
      else:
        (numnz) = _retargs_getbarcsparsity
      idxj = array.array("q")
      idxj.frombytes(idxj_)
      return (numnz,idxj)
    def getbarcsparsity(self,*args,**kwds):
      """
      Get the positions of the nonzero elements in barc.
    
      getbarcsparsity(idxj) -> (numnz)
      getbarcsparsity() -> (numnz,idxj)
        [idxj : array(int64)]  Internal positions of the nonzeros elements in barc.  
        [numnz : int64]  Number of nonzero elements in barc.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 2: return self.__getbarcsparsity_O_2(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getbarcsparsity_O_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getbarasparsity_O_2(self,idxij):
      if idxij is None:
        raise TypeError("Argument idxij may not be None")
      copyback_idxij = False
      if idxij is None:
        idxij_ = None
        memview_idxij = None
      else:
        try:
          memview_idxij = memoryview(idxij)
        except TypeError:
          try:
            _tmparray_idxij = array.array("q",[0 for _ in range(len(idxij))])
          except TypeError:
            raise TypeError("Argument idxij has wrong type") from None
          else:
            memview_idxij = memoryview(_tmparray_idxij)
            copyback_idxij = True
            idxij_ = _tmparray_idxij
        else:
          if memview_idxij.ndim != 1:
            raise TypeError("Argument idxij must be one-dimensional")
          if memview_idxij.format != "q":
            _tmparray_idxij = array.array("q",idxij)
            memview_idxij = memoryview(_tmparray_idxij)
            copyback_idxij = True
            idxij_ = _tmparray_idxij
      _res_getbarasparsity,_retargs_getbarasparsity = self.__obj.getbarasparsity_O_2(memview_idxij)
      if _res_getbarasparsity != 0:
        _,_msg_getbarasparsity = self.__getlasterror(_res_getbarasparsity)
        raise Error(rescode(_res_getbarasparsity),_msg_getbarasparsity)
      else:
        (numnz) = _retargs_getbarasparsity
      if copyback_idxij:
        for __tmp_926 in range(len(idxij)): idxij[__tmp_926] = idxij_[__tmp_926]
      return (numnz)
    def __getbarasparsity_O_1(self):
      idxij_ = bytearray(0)
      _res_getbarasparsity,_retargs_getbarasparsity = self.__obj.getbarasparsity_O_1(idxij_)
      if _res_getbarasparsity != 0:
        _,_msg_getbarasparsity = self.__getlasterror(_res_getbarasparsity)
        raise Error(rescode(_res_getbarasparsity),_msg_getbarasparsity)
      else:
        (numnz) = _retargs_getbarasparsity
      idxij = array.array("q")
      idxij.frombytes(idxij_)
      return (numnz,idxij)
    def getbarasparsity(self,*args,**kwds):
      """
      Obtains the sparsity pattern of the barA matrix.
    
      getbarasparsity(idxij) -> (numnz)
      getbarasparsity() -> (numnz,idxij)
        [idxij : array(int64)]  Position of each nonzero element in the vector representation of barA.  
        [numnz : int64]  Number of nonzero elements in barA.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 2: return self.__getbarasparsity_O_2(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getbarasparsity_O_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getbarcidxinfo_L_2(self,idx):
      _res_getbarcidxinfo,_retargs_getbarcidxinfo = self.__obj.getbarcidxinfo_L_2(idx)
      if _res_getbarcidxinfo != 0:
        _,_msg_getbarcidxinfo = self.__getlasterror(_res_getbarcidxinfo)
        raise Error(rescode(_res_getbarcidxinfo),_msg_getbarcidxinfo)
      else:
        (num) = _retargs_getbarcidxinfo
      return (num)
    def getbarcidxinfo(self,*args,**kwds):
      """
      Obtains information about an element in barc.
    
      getbarcidxinfo(idx) -> (num)
        [idx : int64]  Index of the element for which information should be obtained. The value is an index of a symmetric sparse variable.  
        [num : int64]  Number of terms that appear in the weighted sum that forms the requested element.  
      """
      return self.__getbarcidxinfo_L_2(*args,**kwds)
    def __getbarcidxj_L_2(self,idx):
      _res_getbarcidxj,_retargs_getbarcidxj = self.__obj.getbarcidxj_L_2(idx)
      if _res_getbarcidxj != 0:
        _,_msg_getbarcidxj = self.__getlasterror(_res_getbarcidxj)
        raise Error(rescode(_res_getbarcidxj),_msg_getbarcidxj)
      else:
        (j) = _retargs_getbarcidxj
      return (j)
    def getbarcidxj(self,*args,**kwds):
      """
      Obtains the row index of an element in barc.
    
      getbarcidxj(idx) -> (j)
        [idx : int64]  Index of the element for which information should be obtained.  
        [j : int32]  Row index in barc.  
      """
      return self.__getbarcidxj_L_2(*args,**kwds)
    def __getbarcidx_LOO_4(self,idx,sub,weights):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("q",[0 for _ in range(len(sub))])
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "q":
            _tmparray_sub = array.array("q",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if weights is None:
        raise TypeError("Argument weights may not be None")
      copyback_weights = False
      if weights is None:
        weights_ = None
        memview_weights = None
      else:
        try:
          memview_weights = memoryview(weights)
        except TypeError:
          try:
            _tmparray_weights = array.array("d",[0 for _ in range(len(weights))])
          except TypeError:
            raise TypeError("Argument weights has wrong type") from None
          else:
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
        else:
          if memview_weights.ndim != 1:
            raise TypeError("Argument weights must be one-dimensional")
          if memview_weights.format != "d":
            _tmparray_weights = array.array("d",weights)
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
      _res_getbarcidx,_retargs_getbarcidx = self.__obj.getbarcidx_LOO_4(idx,memview_sub,memview_weights)
      if _res_getbarcidx != 0:
        _,_msg_getbarcidx = self.__getlasterror(_res_getbarcidx)
        raise Error(rescode(_res_getbarcidx),_msg_getbarcidx)
      else:
        (j,num) = _retargs_getbarcidx
      if copyback_sub:
        for __tmp_932 in range(len(sub)): sub[__tmp_932] = sub_[__tmp_932]
      if copyback_weights:
        for __tmp_933 in range(len(weights)): weights[__tmp_933] = weights_[__tmp_933]
      return (j,num)
    def __getbarcidx_LOO_2(self,idx):
      sub_ = bytearray(0)
      weights_ = bytearray(0)
      _res_getbarcidx,_retargs_getbarcidx = self.__obj.getbarcidx_LOO_2(idx,sub_,weights_)
      if _res_getbarcidx != 0:
        _,_msg_getbarcidx = self.__getlasterror(_res_getbarcidx)
        raise Error(rescode(_res_getbarcidx),_msg_getbarcidx)
      else:
        (j,num) = _retargs_getbarcidx
      sub = array.array("q")
      sub.frombytes(sub_)
      weights = array.array("d")
      weights.frombytes(weights_)
      return (j,num,sub,weights)
    def getbarcidx(self,*args,**kwds):
      """
      Obtains information about an element in barc.
    
      getbarcidx(idx,sub,weights) -> (j,num)
      getbarcidx(idx) -> (j,num,sub,weights)
        [idx : int64]  Index of the element for which information should be obtained.  
        [j : int32]  Row index in barc.  
        [num : int64]  Number of terms in the weighted sum.  
        [sub : array(int64)]  Elements appearing the weighted sum.  
        [weights : array(float64)]  Weights of terms in the weighted sum.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getbarcidx_LOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getbarcidx_LOO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getbaraidxinfo_L_2(self,idx):
      _res_getbaraidxinfo,_retargs_getbaraidxinfo = self.__obj.getbaraidxinfo_L_2(idx)
      if _res_getbaraidxinfo != 0:
        _,_msg_getbaraidxinfo = self.__getlasterror(_res_getbaraidxinfo)
        raise Error(rescode(_res_getbaraidxinfo),_msg_getbaraidxinfo)
      else:
        (num) = _retargs_getbaraidxinfo
      return (num)
    def getbaraidxinfo(self,*args,**kwds):
      """
      Obtains the number of terms in the weighted sum that form a particular element in barA.
    
      getbaraidxinfo(idx) -> (num)
        [idx : int64]  The internal position of the element for which information should be obtained.  
        [num : int64]  Number of terms in the weighted sum that form the specified element in barA.  
      """
      return self.__getbaraidxinfo_L_2(*args,**kwds)
    def __getbaraidxij_L_2(self,idx):
      _res_getbaraidxij,_retargs_getbaraidxij = self.__obj.getbaraidxij_L_2(idx)
      if _res_getbaraidxij != 0:
        _,_msg_getbaraidxij = self.__getlasterror(_res_getbaraidxij)
        raise Error(rescode(_res_getbaraidxij),_msg_getbaraidxij)
      else:
        (i,j) = _retargs_getbaraidxij
      return (i,j)
    def getbaraidxij(self,*args,**kwds):
      """
      Obtains information about an element in barA.
    
      getbaraidxij(idx) -> (i,j)
        [i : int32]  Row index of the element at position idx.  
        [idx : int64]  Position of the element in the vectorized form.  
        [j : int32]  Column index of the element at position idx.  
      """
      return self.__getbaraidxij_L_2(*args,**kwds)
    def __getbaraidx_LOO_4(self,idx,sub,weights):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("q",[0 for _ in range(len(sub))])
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "q":
            _tmparray_sub = array.array("q",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if weights is None:
        raise TypeError("Argument weights may not be None")
      copyback_weights = False
      if weights is None:
        weights_ = None
        memview_weights = None
      else:
        try:
          memview_weights = memoryview(weights)
        except TypeError:
          try:
            _tmparray_weights = array.array("d",[0 for _ in range(len(weights))])
          except TypeError:
            raise TypeError("Argument weights has wrong type") from None
          else:
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
        else:
          if memview_weights.ndim != 1:
            raise TypeError("Argument weights must be one-dimensional")
          if memview_weights.format != "d":
            _tmparray_weights = array.array("d",weights)
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
      _res_getbaraidx,_retargs_getbaraidx = self.__obj.getbaraidx_LOO_4(idx,memview_sub,memview_weights)
      if _res_getbaraidx != 0:
        _,_msg_getbaraidx = self.__getlasterror(_res_getbaraidx)
        raise Error(rescode(_res_getbaraidx),_msg_getbaraidx)
      else:
        (i,j,num) = _retargs_getbaraidx
      if copyback_sub:
        for __tmp_940 in range(len(sub)): sub[__tmp_940] = sub_[__tmp_940]
      if copyback_weights:
        for __tmp_941 in range(len(weights)): weights[__tmp_941] = weights_[__tmp_941]
      return (i,j,num)
    def __getbaraidx_LOO_2(self,idx):
      sub_ = bytearray(0)
      weights_ = bytearray(0)
      _res_getbaraidx,_retargs_getbaraidx = self.__obj.getbaraidx_LOO_2(idx,sub_,weights_)
      if _res_getbaraidx != 0:
        _,_msg_getbaraidx = self.__getlasterror(_res_getbaraidx)
        raise Error(rescode(_res_getbaraidx),_msg_getbaraidx)
      else:
        (i,j,num) = _retargs_getbaraidx
      sub = array.array("q")
      sub.frombytes(sub_)
      weights = array.array("d")
      weights.frombytes(weights_)
      return (i,j,num,sub,weights)
    def getbaraidx(self,*args,**kwds):
      """
      Obtains information about an element in barA.
    
      getbaraidx(idx,sub,weights) -> (i,j,num)
      getbaraidx(idx) -> (i,j,num,sub,weights)
        [i : int32]  Row index of the element at position idx.  
        [idx : int64]  Position of the element in the vectorized form.  
        [j : int32]  Column index of the element at position idx.  
        [num : int64]  Number of terms in weighted sum that forms the element.  
        [sub : array(int64)]  A list indexes of the elements from symmetric matrix storage that appear in the weighted sum.  
        [weights : array(float64)]  The weights associated with each term in the weighted sum.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getbaraidx_LOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getbaraidx_LOO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getnumbarcblocktriplets__1(self):
      _res_getnumbarcblocktriplets,_retargs_getnumbarcblocktriplets = self.__obj.getnumbarcblocktriplets__1()
      if _res_getnumbarcblocktriplets != 0:
        _,_msg_getnumbarcblocktriplets = self.__getlasterror(_res_getnumbarcblocktriplets)
        raise Error(rescode(_res_getnumbarcblocktriplets),_msg_getnumbarcblocktriplets)
      else:
        (num) = _retargs_getnumbarcblocktriplets
      return (num)
    def getnumbarcblocktriplets(self,*args,**kwds):
      """
      Obtains an upper bound on the number of elements in the block triplet form of barc.
    
      getnumbarcblocktriplets() -> (num)
        [num : int64]  An upper bound on the number of elements in the block triplet form of barc.  
      """
      return self.__getnumbarcblocktriplets__1(*args,**kwds)
    def __putbarcblocktriplet_OOOO_5(self,subj,subk,subl,valjkl):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if subk is None:
        raise TypeError("Argument subk may not be None")
      copyback_subk = False
      if subk is None:
        subk_ = None
        memview_subk = None
      else:
        try:
          memview_subk = memoryview(subk)
        except TypeError:
          try:
            _tmparray_subk = array.array("i",subk)
          except TypeError:
            raise TypeError("Argument subk has wrong type") from None
          else:
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
        else:
          if memview_subk.ndim != 1:
            raise TypeError("Argument subk must be one-dimensional")
          if memview_subk.format != "i":
            _tmparray_subk = array.array("i",subk)
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
      if subl is None:
        raise TypeError("Argument subl may not be None")
      copyback_subl = False
      if subl is None:
        subl_ = None
        memview_subl = None
      else:
        try:
          memview_subl = memoryview(subl)
        except TypeError:
          try:
            _tmparray_subl = array.array("i",subl)
          except TypeError:
            raise TypeError("Argument subl has wrong type") from None
          else:
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
        else:
          if memview_subl.ndim != 1:
            raise TypeError("Argument subl must be one-dimensional")
          if memview_subl.format != "i":
            _tmparray_subl = array.array("i",subl)
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
      if valjkl is None:
        raise TypeError("Argument valjkl may not be None")
      copyback_valjkl = False
      if valjkl is None:
        valjkl_ = None
        memview_valjkl = None
      else:
        try:
          memview_valjkl = memoryview(valjkl)
        except TypeError:
          try:
            _tmparray_valjkl = array.array("d",valjkl)
          except TypeError:
            raise TypeError("Argument valjkl has wrong type") from None
          else:
            memview_valjkl = memoryview(_tmparray_valjkl)
            copyback_valjkl = True
            valjkl_ = _tmparray_valjkl
        else:
          if memview_valjkl.ndim != 1:
            raise TypeError("Argument valjkl must be one-dimensional")
          if memview_valjkl.format != "d":
            _tmparray_valjkl = array.array("d",valjkl)
            memview_valjkl = memoryview(_tmparray_valjkl)
            copyback_valjkl = True
            valjkl_ = _tmparray_valjkl
      _res_putbarcblocktriplet,_retargs_putbarcblocktriplet = self.__obj.putbarcblocktriplet_OOOO_5(memview_subj,memview_subk,memview_subl,memview_valjkl)
      if _res_putbarcblocktriplet != 0:
        _,_msg_putbarcblocktriplet = self.__getlasterror(_res_putbarcblocktriplet)
        raise Error(rescode(_res_putbarcblocktriplet),_msg_putbarcblocktriplet)
    def putbarcblocktriplet(self,*args,**kwds):
      """
      Inputs barC in block triplet form.
    
      putbarcblocktriplet(subj,subk,subl,valjkl)
        [subj : array(int32)]  Symmetric matrix variable index.  
        [subk : array(int32)]  Block row index.  
        [subl : array(int32)]  Block column index.  
        [valjkl : array(float64)]  The numerical value associated with each block triplet.  
      """
      return self.__putbarcblocktriplet_OOOO_5(*args,**kwds)
    def __getbarcblocktriplet_OOOO_5(self,subj,subk,subl,valjkl):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",[0 for _ in range(len(subj))])
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if subk is None:
        raise TypeError("Argument subk may not be None")
      copyback_subk = False
      if subk is None:
        subk_ = None
        memview_subk = None
      else:
        try:
          memview_subk = memoryview(subk)
        except TypeError:
          try:
            _tmparray_subk = array.array("i",[0 for _ in range(len(subk))])
          except TypeError:
            raise TypeError("Argument subk has wrong type") from None
          else:
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
        else:
          if memview_subk.ndim != 1:
            raise TypeError("Argument subk must be one-dimensional")
          if memview_subk.format != "i":
            _tmparray_subk = array.array("i",subk)
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
      if subl is None:
        raise TypeError("Argument subl may not be None")
      copyback_subl = False
      if subl is None:
        subl_ = None
        memview_subl = None
      else:
        try:
          memview_subl = memoryview(subl)
        except TypeError:
          try:
            _tmparray_subl = array.array("i",[0 for _ in range(len(subl))])
          except TypeError:
            raise TypeError("Argument subl has wrong type") from None
          else:
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
        else:
          if memview_subl.ndim != 1:
            raise TypeError("Argument subl must be one-dimensional")
          if memview_subl.format != "i":
            _tmparray_subl = array.array("i",subl)
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
      if valjkl is None:
        raise TypeError("Argument valjkl may not be None")
      copyback_valjkl = False
      if valjkl is None:
        valjkl_ = None
        memview_valjkl = None
      else:
        try:
          memview_valjkl = memoryview(valjkl)
        except TypeError:
          try:
            _tmparray_valjkl = array.array("d",[0 for _ in range(len(valjkl))])
          except TypeError:
            raise TypeError("Argument valjkl has wrong type") from None
          else:
            memview_valjkl = memoryview(_tmparray_valjkl)
            copyback_valjkl = True
            valjkl_ = _tmparray_valjkl
        else:
          if memview_valjkl.ndim != 1:
            raise TypeError("Argument valjkl must be one-dimensional")
          if memview_valjkl.format != "d":
            _tmparray_valjkl = array.array("d",valjkl)
            memview_valjkl = memoryview(_tmparray_valjkl)
            copyback_valjkl = True
            valjkl_ = _tmparray_valjkl
      _res_getbarcblocktriplet,_retargs_getbarcblocktriplet = self.__obj.getbarcblocktriplet_OOOO_5(memview_subj,memview_subk,memview_subl,memview_valjkl)
      if _res_getbarcblocktriplet != 0:
        _,_msg_getbarcblocktriplet = self.__getlasterror(_res_getbarcblocktriplet)
        raise Error(rescode(_res_getbarcblocktriplet),_msg_getbarcblocktriplet)
      else:
        (num) = _retargs_getbarcblocktriplet
      if copyback_subj:
        for __tmp_956 in range(len(subj)): subj[__tmp_956] = subj_[__tmp_956]
      if copyback_subk:
        for __tmp_957 in range(len(subk)): subk[__tmp_957] = subk_[__tmp_957]
      if copyback_subl:
        for __tmp_958 in range(len(subl)): subl[__tmp_958] = subl_[__tmp_958]
      if copyback_valjkl:
        for __tmp_959 in range(len(valjkl)): valjkl[__tmp_959] = valjkl_[__tmp_959]
      return (num)
    def __getbarcblocktriplet_OOOO_1(self):
      subj_ = bytearray(0)
      subk_ = bytearray(0)
      subl_ = bytearray(0)
      valjkl_ = bytearray(0)
      _res_getbarcblocktriplet,_retargs_getbarcblocktriplet = self.__obj.getbarcblocktriplet_OOOO_1(subj_,subk_,subl_,valjkl_)
      if _res_getbarcblocktriplet != 0:
        _,_msg_getbarcblocktriplet = self.__getlasterror(_res_getbarcblocktriplet)
        raise Error(rescode(_res_getbarcblocktriplet),_msg_getbarcblocktriplet)
      else:
        (num) = _retargs_getbarcblocktriplet
      subj = array.array("i")
      subj.frombytes(subj_)
      subk = array.array("i")
      subk.frombytes(subk_)
      subl = array.array("i")
      subl.frombytes(subl_)
      valjkl = array.array("d")
      valjkl.frombytes(valjkl_)
      return (num,subj,subk,subl,valjkl)
    def getbarcblocktriplet(self,*args,**kwds):
      """
      Obtains barC in block triplet form.
    
      getbarcblocktriplet(subj,subk,subl,valjkl) -> (num)
      getbarcblocktriplet() -> (num,subj,subk,subl,valjkl)
        [num : int64]  Number of elements in the block triplet form.  
        [subj : array(int32)]  Symmetric matrix variable index.  
        [subk : array(int32)]  Block row index.  
        [subl : array(int32)]  Block column index.  
        [valjkl : array(float64)]  The numerical value associated with each block triplet.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getbarcblocktriplet_OOOO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getbarcblocktriplet_OOOO_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __putbarablocktriplet_OOOOO_6(self,subi,subj,subk,subl,valijkl):
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",subi)
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if subk is None:
        raise TypeError("Argument subk may not be None")
      copyback_subk = False
      if subk is None:
        subk_ = None
        memview_subk = None
      else:
        try:
          memview_subk = memoryview(subk)
        except TypeError:
          try:
            _tmparray_subk = array.array("i",subk)
          except TypeError:
            raise TypeError("Argument subk has wrong type") from None
          else:
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
        else:
          if memview_subk.ndim != 1:
            raise TypeError("Argument subk must be one-dimensional")
          if memview_subk.format != "i":
            _tmparray_subk = array.array("i",subk)
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
      if subl is None:
        raise TypeError("Argument subl may not be None")
      copyback_subl = False
      if subl is None:
        subl_ = None
        memview_subl = None
      else:
        try:
          memview_subl = memoryview(subl)
        except TypeError:
          try:
            _tmparray_subl = array.array("i",subl)
          except TypeError:
            raise TypeError("Argument subl has wrong type") from None
          else:
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
        else:
          if memview_subl.ndim != 1:
            raise TypeError("Argument subl must be one-dimensional")
          if memview_subl.format != "i":
            _tmparray_subl = array.array("i",subl)
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
      if valijkl is None:
        raise TypeError("Argument valijkl may not be None")
      copyback_valijkl = False
      if valijkl is None:
        valijkl_ = None
        memview_valijkl = None
      else:
        try:
          memview_valijkl = memoryview(valijkl)
        except TypeError:
          try:
            _tmparray_valijkl = array.array("d",valijkl)
          except TypeError:
            raise TypeError("Argument valijkl has wrong type") from None
          else:
            memview_valijkl = memoryview(_tmparray_valijkl)
            copyback_valijkl = True
            valijkl_ = _tmparray_valijkl
        else:
          if memview_valijkl.ndim != 1:
            raise TypeError("Argument valijkl must be one-dimensional")
          if memview_valijkl.format != "d":
            _tmparray_valijkl = array.array("d",valijkl)
            memview_valijkl = memoryview(_tmparray_valijkl)
            copyback_valijkl = True
            valijkl_ = _tmparray_valijkl
      _res_putbarablocktriplet,_retargs_putbarablocktriplet = self.__obj.putbarablocktriplet_OOOOO_6(memview_subi,memview_subj,memview_subk,memview_subl,memview_valijkl)
      if _res_putbarablocktriplet != 0:
        _,_msg_putbarablocktriplet = self.__getlasterror(_res_putbarablocktriplet)
        raise Error(rescode(_res_putbarablocktriplet),_msg_putbarablocktriplet)
    def putbarablocktriplet(self,*args,**kwds):
      """
      Inputs barA in block triplet form.
    
      putbarablocktriplet(subi,subj,subk,subl,valijkl)
        [subi : array(int32)]  Constraint index.  
        [subj : array(int32)]  Symmetric matrix variable index.  
        [subk : array(int32)]  Block row index.  
        [subl : array(int32)]  Block column index.  
        [valijkl : array(float64)]  The numerical value associated with each block triplet.  
      """
      return self.__putbarablocktriplet_OOOOO_6(*args,**kwds)
    def __getnumbarablocktriplets__1(self):
      _res_getnumbarablocktriplets,_retargs_getnumbarablocktriplets = self.__obj.getnumbarablocktriplets__1()
      if _res_getnumbarablocktriplets != 0:
        _,_msg_getnumbarablocktriplets = self.__getlasterror(_res_getnumbarablocktriplets)
        raise Error(rescode(_res_getnumbarablocktriplets),_msg_getnumbarablocktriplets)
      else:
        (num) = _retargs_getnumbarablocktriplets
      return (num)
    def getnumbarablocktriplets(self,*args,**kwds):
      """
      Obtains an upper bound on the number of scalar elements in the block triplet form of bara.
    
      getnumbarablocktriplets() -> (num)
        [num : int64]  An upper bound on the number of elements in the block triplet form of bara.  
      """
      return self.__getnumbarablocktriplets__1(*args,**kwds)
    def __getbarablocktriplet_OOOOO_6(self,subi,subj,subk,subl,valijkl):
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",[0 for _ in range(len(subi))])
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",[0 for _ in range(len(subj))])
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if subk is None:
        raise TypeError("Argument subk may not be None")
      copyback_subk = False
      if subk is None:
        subk_ = None
        memview_subk = None
      else:
        try:
          memview_subk = memoryview(subk)
        except TypeError:
          try:
            _tmparray_subk = array.array("i",[0 for _ in range(len(subk))])
          except TypeError:
            raise TypeError("Argument subk has wrong type") from None
          else:
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
        else:
          if memview_subk.ndim != 1:
            raise TypeError("Argument subk must be one-dimensional")
          if memview_subk.format != "i":
            _tmparray_subk = array.array("i",subk)
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
      if subl is None:
        raise TypeError("Argument subl may not be None")
      copyback_subl = False
      if subl is None:
        subl_ = None
        memview_subl = None
      else:
        try:
          memview_subl = memoryview(subl)
        except TypeError:
          try:
            _tmparray_subl = array.array("i",[0 for _ in range(len(subl))])
          except TypeError:
            raise TypeError("Argument subl has wrong type") from None
          else:
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
        else:
          if memview_subl.ndim != 1:
            raise TypeError("Argument subl must be one-dimensional")
          if memview_subl.format != "i":
            _tmparray_subl = array.array("i",subl)
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
      if valijkl is None:
        raise TypeError("Argument valijkl may not be None")
      copyback_valijkl = False
      if valijkl is None:
        valijkl_ = None
        memview_valijkl = None
      else:
        try:
          memview_valijkl = memoryview(valijkl)
        except TypeError:
          try:
            _tmparray_valijkl = array.array("d",[0 for _ in range(len(valijkl))])
          except TypeError:
            raise TypeError("Argument valijkl has wrong type") from None
          else:
            memview_valijkl = memoryview(_tmparray_valijkl)
            copyback_valijkl = True
            valijkl_ = _tmparray_valijkl
        else:
          if memview_valijkl.ndim != 1:
            raise TypeError("Argument valijkl must be one-dimensional")
          if memview_valijkl.format != "d":
            _tmparray_valijkl = array.array("d",valijkl)
            memview_valijkl = memoryview(_tmparray_valijkl)
            copyback_valijkl = True
            valijkl_ = _tmparray_valijkl
      _res_getbarablocktriplet,_retargs_getbarablocktriplet = self.__obj.getbarablocktriplet_OOOOO_6(memview_subi,memview_subj,memview_subk,memview_subl,memview_valijkl)
      if _res_getbarablocktriplet != 0:
        _,_msg_getbarablocktriplet = self.__getlasterror(_res_getbarablocktriplet)
        raise Error(rescode(_res_getbarablocktriplet),_msg_getbarablocktriplet)
      else:
        (num) = _retargs_getbarablocktriplet
      if copyback_subi:
        for __tmp_978 in range(len(subi)): subi[__tmp_978] = subi_[__tmp_978]
      if copyback_subj:
        for __tmp_979 in range(len(subj)): subj[__tmp_979] = subj_[__tmp_979]
      if copyback_subk:
        for __tmp_980 in range(len(subk)): subk[__tmp_980] = subk_[__tmp_980]
      if copyback_subl:
        for __tmp_981 in range(len(subl)): subl[__tmp_981] = subl_[__tmp_981]
      if copyback_valijkl:
        for __tmp_982 in range(len(valijkl)): valijkl[__tmp_982] = valijkl_[__tmp_982]
      return (num)
    def __getbarablocktriplet_OOOOO_1(self):
      subi_ = bytearray(0)
      subj_ = bytearray(0)
      subk_ = bytearray(0)
      subl_ = bytearray(0)
      valijkl_ = bytearray(0)
      _res_getbarablocktriplet,_retargs_getbarablocktriplet = self.__obj.getbarablocktriplet_OOOOO_1(subi_,subj_,subk_,subl_,valijkl_)
      if _res_getbarablocktriplet != 0:
        _,_msg_getbarablocktriplet = self.__getlasterror(_res_getbarablocktriplet)
        raise Error(rescode(_res_getbarablocktriplet),_msg_getbarablocktriplet)
      else:
        (num) = _retargs_getbarablocktriplet
      subi = array.array("i")
      subi.frombytes(subi_)
      subj = array.array("i")
      subj.frombytes(subj_)
      subk = array.array("i")
      subk.frombytes(subk_)
      subl = array.array("i")
      subl.frombytes(subl_)
      valijkl = array.array("d")
      valijkl.frombytes(valijkl_)
      return (num,subi,subj,subk,subl,valijkl)
    def getbarablocktriplet(self,*args,**kwds):
      """
      Obtains barA in block triplet form.
    
      getbarablocktriplet(subi,subj,subk,subl,valijkl) -> (num)
      getbarablocktriplet() -> (num,subi,subj,subk,subl,valijkl)
        [num : int64]  Number of elements in the block triplet form.  
        [subi : array(int32)]  Constraint index.  
        [subj : array(int32)]  Symmetric matrix variable index.  
        [subk : array(int32)]  Block row index.  
        [subl : array(int32)]  Block column index.  
        [valijkl : array(float64)]  The numerical value associated with each block triplet.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__getbarablocktriplet_OOOOO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getbarablocktriplet_OOOOO_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __putmaxnumafe_L_2(self,maxnumafe):
      _res_putmaxnumafe,_retargs_putmaxnumafe = self.__obj.putmaxnumafe_L_2(maxnumafe)
      if _res_putmaxnumafe != 0:
        _,_msg_putmaxnumafe = self.__getlasterror(_res_putmaxnumafe)
        raise Error(rescode(_res_putmaxnumafe),_msg_putmaxnumafe)
    def putmaxnumafe(self,*args,**kwds):
      """
      Sets the number of preallocated affine expressions in the optimization task.
    
      putmaxnumafe(maxnumafe)
        [maxnumafe : int64]  Number of preallocated affine expressions.  
      """
      return self.__putmaxnumafe_L_2(*args,**kwds)
    def __getnumafe__1(self):
      _res_getnumafe,_retargs_getnumafe = self.__obj.getnumafe__1()
      if _res_getnumafe != 0:
        _,_msg_getnumafe = self.__getlasterror(_res_getnumafe)
        raise Error(rescode(_res_getnumafe),_msg_getnumafe)
      else:
        (numafe) = _retargs_getnumafe
      return (numafe)
    def getnumafe(self,*args,**kwds):
      """
      Obtains the number of affine expressions.
    
      getnumafe() -> (numafe)
        [numafe : int64]  Number of affine expressions.  
      """
      return self.__getnumafe__1(*args,**kwds)
    def __appendafes_L_2(self,num):
      _res_appendafes,_retargs_appendafes = self.__obj.appendafes_L_2(num)
      if _res_appendafes != 0:
        _,_msg_appendafes = self.__getlasterror(_res_appendafes)
        raise Error(rescode(_res_appendafes),_msg_appendafes)
    def appendafes(self,*args,**kwds):
      """
      Appends a number of empty affine expressions to the optimization task.
    
      appendafes(num)
        [num : int64]  Number of empty affine expressions which should be appended.  
      """
      return self.__appendafes_L_2(*args,**kwds)
    def __putafefentry_Lid_4(self,afeidx,varidx,value):
      _res_putafefentry,_retargs_putafefentry = self.__obj.putafefentry_Lid_4(afeidx,varidx,value)
      if _res_putafefentry != 0:
        _,_msg_putafefentry = self.__getlasterror(_res_putafefentry)
        raise Error(rescode(_res_putafefentry),_msg_putafefentry)
    def putafefentry(self,*args,**kwds):
      """
      Replaces one entry in F.
    
      putafefentry(afeidx,varidx,value)
        [afeidx : int64]  Row index in F.  
        [value : float64]  Value of the entry.  
        [varidx : int32]  Column index in F.  
      """
      return self.__putafefentry_Lid_4(*args,**kwds)
    def __putafefentrylist_OOO_4(self,afeidx,varidx,val):
      if afeidx is None:
        raise TypeError("Argument afeidx may not be None")
      copyback_afeidx = False
      if afeidx is None:
        afeidx_ = None
        memview_afeidx = None
      else:
        try:
          memview_afeidx = memoryview(afeidx)
        except TypeError:
          try:
            _tmparray_afeidx = array.array("q",afeidx)
          except TypeError:
            raise TypeError("Argument afeidx has wrong type") from None
          else:
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
        else:
          if memview_afeidx.ndim != 1:
            raise TypeError("Argument afeidx must be one-dimensional")
          if memview_afeidx.format != "q":
            _tmparray_afeidx = array.array("q",afeidx)
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
      if varidx is None:
        raise TypeError("Argument varidx may not be None")
      copyback_varidx = False
      if varidx is None:
        varidx_ = None
        memview_varidx = None
      else:
        try:
          memview_varidx = memoryview(varidx)
        except TypeError:
          try:
            _tmparray_varidx = array.array("i",varidx)
          except TypeError:
            raise TypeError("Argument varidx has wrong type") from None
          else:
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
        else:
          if memview_varidx.ndim != 1:
            raise TypeError("Argument varidx must be one-dimensional")
          if memview_varidx.format != "i":
            _tmparray_varidx = array.array("i",varidx)
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
      if val is None:
        raise TypeError("Argument val may not be None")
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",val)
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_putafefentrylist,_retargs_putafefentrylist = self.__obj.putafefentrylist_OOO_4(memview_afeidx,memview_varidx,memview_val)
      if _res_putafefentrylist != 0:
        _,_msg_putafefentrylist = self.__getlasterror(_res_putafefentrylist)
        raise Error(rescode(_res_putafefentrylist),_msg_putafefentrylist)
    def putafefentrylist(self,*args,**kwds):
      """
      Replaces a list of entries in F.
    
      putafefentrylist(afeidx,varidx,val)
        [afeidx : array(int64)]  Row indices in F.  
        [val : array(float64)]  Values of the entries in F.  
        [varidx : array(int32)]  Column indices in F.  
      """
      return self.__putafefentrylist_OOO_4(*args,**kwds)
    def __emptyafefrow_L_2(self,afeidx):
      _res_emptyafefrow,_retargs_emptyafefrow = self.__obj.emptyafefrow_L_2(afeidx)
      if _res_emptyafefrow != 0:
        _,_msg_emptyafefrow = self.__getlasterror(_res_emptyafefrow)
        raise Error(rescode(_res_emptyafefrow),_msg_emptyafefrow)
    def emptyafefrow(self,*args,**kwds):
      """
      Clears a row in F.
    
      emptyafefrow(afeidx)
        [afeidx : int64]  Row index.  
      """
      return self.__emptyafefrow_L_2(*args,**kwds)
    def __emptyafefcol_i_2(self,varidx):
      _res_emptyafefcol,_retargs_emptyafefcol = self.__obj.emptyafefcol_i_2(varidx)
      if _res_emptyafefcol != 0:
        _,_msg_emptyafefcol = self.__getlasterror(_res_emptyafefcol)
        raise Error(rescode(_res_emptyafefcol),_msg_emptyafefcol)
    def emptyafefcol(self,*args,**kwds):
      """
      Clears a column in F.
    
      emptyafefcol(varidx)
        [varidx : int32]  Variable index.  
      """
      return self.__emptyafefcol_i_2(*args,**kwds)
    def __emptyafefrowlist_O_2(self,afeidx):
      if afeidx is None:
        raise TypeError("Argument afeidx may not be None")
      copyback_afeidx = False
      if afeidx is None:
        afeidx_ = None
        memview_afeidx = None
      else:
        try:
          memview_afeidx = memoryview(afeidx)
        except TypeError:
          try:
            _tmparray_afeidx = array.array("q",afeidx)
          except TypeError:
            raise TypeError("Argument afeidx has wrong type") from None
          else:
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
        else:
          if memview_afeidx.ndim != 1:
            raise TypeError("Argument afeidx must be one-dimensional")
          if memview_afeidx.format != "q":
            _tmparray_afeidx = array.array("q",afeidx)
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
      _res_emptyafefrowlist,_retargs_emptyafefrowlist = self.__obj.emptyafefrowlist_O_2(memview_afeidx)
      if _res_emptyafefrowlist != 0:
        _,_msg_emptyafefrowlist = self.__getlasterror(_res_emptyafefrowlist)
        raise Error(rescode(_res_emptyafefrowlist),_msg_emptyafefrowlist)
    def emptyafefrowlist(self,*args,**kwds):
      """
      Clears rows in F.
    
      emptyafefrowlist(afeidx)
        [afeidx : array(int64)]  Indices of rows in F to clear.  
      """
      return self.__emptyafefrowlist_O_2(*args,**kwds)
    def __emptyafefcollist_O_2(self,varidx):
      if varidx is None:
        raise TypeError("Argument varidx may not be None")
      copyback_varidx = False
      if varidx is None:
        varidx_ = None
        memview_varidx = None
      else:
        try:
          memview_varidx = memoryview(varidx)
        except TypeError:
          try:
            _tmparray_varidx = array.array("i",varidx)
          except TypeError:
            raise TypeError("Argument varidx has wrong type") from None
          else:
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
        else:
          if memview_varidx.ndim != 1:
            raise TypeError("Argument varidx must be one-dimensional")
          if memview_varidx.format != "i":
            _tmparray_varidx = array.array("i",varidx)
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
      _res_emptyafefcollist,_retargs_emptyafefcollist = self.__obj.emptyafefcollist_O_2(memview_varidx)
      if _res_emptyafefcollist != 0:
        _,_msg_emptyafefcollist = self.__getlasterror(_res_emptyafefcollist)
        raise Error(rescode(_res_emptyafefcollist),_msg_emptyafefcollist)
    def emptyafefcollist(self,*args,**kwds):
      """
      Clears columns in F.
    
      emptyafefcollist(varidx)
        [varidx : array(int32)]  Indices of variables in F to clear.  
      """
      return self.__emptyafefcollist_O_2(*args,**kwds)
    def __putafefrow_LOO_4(self,afeidx,varidx,val):
      if varidx is None:
        raise TypeError("Argument varidx may not be None")
      copyback_varidx = False
      if varidx is None:
        varidx_ = None
        memview_varidx = None
      else:
        try:
          memview_varidx = memoryview(varidx)
        except TypeError:
          try:
            _tmparray_varidx = array.array("i",varidx)
          except TypeError:
            raise TypeError("Argument varidx has wrong type") from None
          else:
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
        else:
          if memview_varidx.ndim != 1:
            raise TypeError("Argument varidx must be one-dimensional")
          if memview_varidx.format != "i":
            _tmparray_varidx = array.array("i",varidx)
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
      if val is None:
        raise TypeError("Argument val may not be None")
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",val)
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_putafefrow,_retargs_putafefrow = self.__obj.putafefrow_LOO_4(afeidx,memview_varidx,memview_val)
      if _res_putafefrow != 0:
        _,_msg_putafefrow = self.__getlasterror(_res_putafefrow)
        raise Error(rescode(_res_putafefrow),_msg_putafefrow)
    def putafefrow(self,*args,**kwds):
      """
      Replaces all elements in one row of the F matrix in the affine expressions.
    
      putafefrow(afeidx,varidx,val)
        [afeidx : int64]  Row index.  
        [val : array(float64)]  New non-zero values in the row.  
        [varidx : array(int32)]  Column indexes of non-zero values in the row.  
      """
      return self.__putafefrow_LOO_4(*args,**kwds)
    def __putafefrowlist_OOOOO_6(self,afeidx,numnzrow,ptrrow,varidx,val):
      if afeidx is None:
        raise TypeError("Argument afeidx may not be None")
      copyback_afeidx = False
      if afeidx is None:
        afeidx_ = None
        memview_afeidx = None
      else:
        try:
          memview_afeidx = memoryview(afeidx)
        except TypeError:
          try:
            _tmparray_afeidx = array.array("q",afeidx)
          except TypeError:
            raise TypeError("Argument afeidx has wrong type") from None
          else:
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
        else:
          if memview_afeidx.ndim != 1:
            raise TypeError("Argument afeidx must be one-dimensional")
          if memview_afeidx.format != "q":
            _tmparray_afeidx = array.array("q",afeidx)
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
      if numnzrow is None:
        raise TypeError("Argument numnzrow may not be None")
      copyback_numnzrow = False
      if numnzrow is None:
        numnzrow_ = None
        memview_numnzrow = None
      else:
        try:
          memview_numnzrow = memoryview(numnzrow)
        except TypeError:
          try:
            _tmparray_numnzrow = array.array("i",numnzrow)
          except TypeError:
            raise TypeError("Argument numnzrow has wrong type") from None
          else:
            memview_numnzrow = memoryview(_tmparray_numnzrow)
            copyback_numnzrow = True
            numnzrow_ = _tmparray_numnzrow
        else:
          if memview_numnzrow.ndim != 1:
            raise TypeError("Argument numnzrow must be one-dimensional")
          if memview_numnzrow.format != "i":
            _tmparray_numnzrow = array.array("i",numnzrow)
            memview_numnzrow = memoryview(_tmparray_numnzrow)
            copyback_numnzrow = True
            numnzrow_ = _tmparray_numnzrow
      if ptrrow is None:
        raise TypeError("Argument ptrrow may not be None")
      copyback_ptrrow = False
      if ptrrow is None:
        ptrrow_ = None
        memview_ptrrow = None
      else:
        try:
          memview_ptrrow = memoryview(ptrrow)
        except TypeError:
          try:
            _tmparray_ptrrow = array.array("q",ptrrow)
          except TypeError:
            raise TypeError("Argument ptrrow has wrong type") from None
          else:
            memview_ptrrow = memoryview(_tmparray_ptrrow)
            copyback_ptrrow = True
            ptrrow_ = _tmparray_ptrrow
        else:
          if memview_ptrrow.ndim != 1:
            raise TypeError("Argument ptrrow must be one-dimensional")
          if memview_ptrrow.format != "q":
            _tmparray_ptrrow = array.array("q",ptrrow)
            memview_ptrrow = memoryview(_tmparray_ptrrow)
            copyback_ptrrow = True
            ptrrow_ = _tmparray_ptrrow
      if varidx is None:
        raise TypeError("Argument varidx may not be None")
      copyback_varidx = False
      if varidx is None:
        varidx_ = None
        memview_varidx = None
      else:
        try:
          memview_varidx = memoryview(varidx)
        except TypeError:
          try:
            _tmparray_varidx = array.array("i",varidx)
          except TypeError:
            raise TypeError("Argument varidx has wrong type") from None
          else:
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
        else:
          if memview_varidx.ndim != 1:
            raise TypeError("Argument varidx must be one-dimensional")
          if memview_varidx.format != "i":
            _tmparray_varidx = array.array("i",varidx)
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
      if val is None:
        raise TypeError("Argument val may not be None")
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",val)
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_putafefrowlist,_retargs_putafefrowlist = self.__obj.putafefrowlist_OOOOO_6(memview_afeidx,memview_numnzrow,memview_ptrrow,memview_varidx,memview_val)
      if _res_putafefrowlist != 0:
        _,_msg_putafefrowlist = self.__getlasterror(_res_putafefrowlist)
        raise Error(rescode(_res_putafefrowlist),_msg_putafefrowlist)
    def putafefrowlist(self,*args,**kwds):
      """
      Replaces all elements in a number of rows of the F matrix in the affine expressions.
    
      putafefrowlist(afeidx,numnzrow,ptrrow,varidx,val)
        [afeidx : array(int64)]  Row indices.  
        [numnzrow : array(int32)]  Number of non-zeros in each row.  
        [ptrrow : array(int64)]  Pointer to the first nonzero in each row.  
        [val : array(float64)]  New non-zero values in the rows.  
        [varidx : array(int32)]  Column indexes of non-zero values.  
      """
      return self.__putafefrowlist_OOOOO_6(*args,**kwds)
    def __putafefcol_iOO_4(self,varidx,afeidx,val):
      if afeidx is None:
        raise TypeError("Argument afeidx may not be None")
      copyback_afeidx = False
      if afeidx is None:
        afeidx_ = None
        memview_afeidx = None
      else:
        try:
          memview_afeidx = memoryview(afeidx)
        except TypeError:
          try:
            _tmparray_afeidx = array.array("q",afeidx)
          except TypeError:
            raise TypeError("Argument afeidx has wrong type") from None
          else:
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
        else:
          if memview_afeidx.ndim != 1:
            raise TypeError("Argument afeidx must be one-dimensional")
          if memview_afeidx.format != "q":
            _tmparray_afeidx = array.array("q",afeidx)
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
      if val is None:
        raise TypeError("Argument val may not be None")
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",val)
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_putafefcol,_retargs_putafefcol = self.__obj.putafefcol_iOO_4(varidx,memview_afeidx,memview_val)
      if _res_putafefcol != 0:
        _,_msg_putafefcol = self.__getlasterror(_res_putafefcol)
        raise Error(rescode(_res_putafefcol),_msg_putafefcol)
    def putafefcol(self,*args,**kwds):
      """
      Replaces all elements in one column of the F matrix in the affine expressions.
    
      putafefcol(varidx,afeidx,val)
        [afeidx : array(int64)]  Row indexes of non-zero values in the column.  
        [val : array(float64)]  New non-zero values in the column.  
        [varidx : int32]  Column index.  
      """
      return self.__putafefcol_iOO_4(*args,**kwds)
    def __getafefrownumnz_L_2(self,afeidx):
      _res_getafefrownumnz,_retargs_getafefrownumnz = self.__obj.getafefrownumnz_L_2(afeidx)
      if _res_getafefrownumnz != 0:
        _,_msg_getafefrownumnz = self.__getlasterror(_res_getafefrownumnz)
        raise Error(rescode(_res_getafefrownumnz),_msg_getafefrownumnz)
      else:
        (numnz) = _retargs_getafefrownumnz
      return (numnz)
    def getafefrownumnz(self,*args,**kwds):
      """
      Obtains the number of nonzeros in a row of F.
    
      getafefrownumnz(afeidx) -> (numnz)
        [afeidx : int64]  Row index.  
        [numnz : int32]  Number of non-zeros in the row.  
      """
      return self.__getafefrownumnz_L_2(*args,**kwds)
    def __getafefnumnz__1(self):
      _res_getafefnumnz,_retargs_getafefnumnz = self.__obj.getafefnumnz__1()
      if _res_getafefnumnz != 0:
        _,_msg_getafefnumnz = self.__getlasterror(_res_getafefnumnz)
        raise Error(rescode(_res_getafefnumnz),_msg_getafefnumnz)
      else:
        (numnz) = _retargs_getafefnumnz
      return (numnz)
    def getafefnumnz(self,*args,**kwds):
      """
      Obtains the total number of nonzeros in F.
    
      getafefnumnz() -> (numnz)
        [numnz : int64]  Number of nonzeros in F.  
      """
      return self.__getafefnumnz__1(*args,**kwds)
    def __getafefrow_LOO_4(self,afeidx,varidx,val):
      copyback_varidx = False
      if varidx is None:
        varidx_ = None
        memview_varidx = None
      else:
        try:
          memview_varidx = memoryview(varidx)
        except TypeError:
          try:
            _tmparray_varidx = array.array("i",[0 for _ in range(len(varidx))])
          except TypeError:
            raise TypeError("Argument varidx has wrong type") from None
          else:
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
        else:
          if memview_varidx.ndim != 1:
            raise TypeError("Argument varidx must be one-dimensional")
          if memview_varidx.format != "i":
            _tmparray_varidx = array.array("i",varidx)
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",[0 for _ in range(len(val))])
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_getafefrow,_retargs_getafefrow = self.__obj.getafefrow_LOO_4(afeidx,memview_varidx,memview_val)
      if _res_getafefrow != 0:
        _,_msg_getafefrow = self.__getlasterror(_res_getafefrow)
        raise Error(rescode(_res_getafefrow),_msg_getafefrow)
      else:
        (numnz) = _retargs_getafefrow
      if copyback_varidx:
        for __tmp_1020 in range(len(varidx)): varidx[__tmp_1020] = varidx_[__tmp_1020]
      if copyback_val:
        for __tmp_1023 in range(len(val)): val[__tmp_1023] = val_[__tmp_1023]
      return (numnz)
    def __getafefrow_LOO_2(self,afeidx):
      varidx_ = bytearray(0)
      val_ = bytearray(0)
      _res_getafefrow,_retargs_getafefrow = self.__obj.getafefrow_LOO_2(afeidx,varidx_,val_)
      if _res_getafefrow != 0:
        _,_msg_getafefrow = self.__getlasterror(_res_getafefrow)
        raise Error(rescode(_res_getafefrow),_msg_getafefrow)
      else:
        (numnz) = _retargs_getafefrow
      varidx = array.array("i")
      varidx.frombytes(varidx_)
      val = array.array("d")
      val.frombytes(val_)
      return (numnz,varidx,val)
    def getafefrow(self,*args,**kwds):
      """
      Obtains one row of F in sparse format.
    
      getafefrow(afeidx,varidx,val) -> (numnz)
      getafefrow(afeidx) -> (numnz,varidx,val)
        [afeidx : int64]  Row index.  
        [numnz : int32]  Number of non-zeros in the row obtained.  
        [val : array(float64)]  Values of the non-zeros in the row obtained.  
        [varidx : array(int32)]  Column indices of the non-zeros in the row obtained.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getafefrow_LOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getafefrow_LOO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getafeftrip_OOO_4(self,afeidx,varidx,val):
      if afeidx is None:
        raise TypeError("Argument afeidx may not be None")
      copyback_afeidx = False
      if afeidx is None:
        afeidx_ = None
        memview_afeidx = None
      else:
        try:
          memview_afeidx = memoryview(afeidx)
        except TypeError:
          try:
            _tmparray_afeidx = array.array("q",[0 for _ in range(len(afeidx))])
          except TypeError:
            raise TypeError("Argument afeidx has wrong type") from None
          else:
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
        else:
          if memview_afeidx.ndim != 1:
            raise TypeError("Argument afeidx must be one-dimensional")
          if memview_afeidx.format != "q":
            _tmparray_afeidx = array.array("q",afeidx)
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
      if varidx is None:
        raise TypeError("Argument varidx may not be None")
      copyback_varidx = False
      if varidx is None:
        varidx_ = None
        memview_varidx = None
      else:
        try:
          memview_varidx = memoryview(varidx)
        except TypeError:
          try:
            _tmparray_varidx = array.array("i",[0 for _ in range(len(varidx))])
          except TypeError:
            raise TypeError("Argument varidx has wrong type") from None
          else:
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
        else:
          if memview_varidx.ndim != 1:
            raise TypeError("Argument varidx must be one-dimensional")
          if memview_varidx.format != "i":
            _tmparray_varidx = array.array("i",varidx)
            memview_varidx = memoryview(_tmparray_varidx)
            copyback_varidx = True
            varidx_ = _tmparray_varidx
      if val is None:
        raise TypeError("Argument val may not be None")
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",[0 for _ in range(len(val))])
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_getafeftrip,_retargs_getafeftrip = self.__obj.getafeftrip_OOO_4(memview_afeidx,memview_varidx,memview_val)
      if _res_getafeftrip != 0:
        _,_msg_getafeftrip = self.__getlasterror(_res_getafeftrip)
        raise Error(rescode(_res_getafeftrip),_msg_getafeftrip)
      if copyback_afeidx:
        for __tmp_1032 in range(len(afeidx)): afeidx[__tmp_1032] = afeidx_[__tmp_1032]
      if copyback_varidx:
        for __tmp_1035 in range(len(varidx)): varidx[__tmp_1035] = varidx_[__tmp_1035]
      if copyback_val:
        for __tmp_1038 in range(len(val)): val[__tmp_1038] = val_[__tmp_1038]
    def __getafeftrip_OOO_1(self):
      afeidx_ = bytearray(0)
      varidx_ = bytearray(0)
      val_ = bytearray(0)
      _res_getafeftrip,_retargs_getafeftrip = self.__obj.getafeftrip_OOO_1(afeidx_,varidx_,val_)
      if _res_getafeftrip != 0:
        _,_msg_getafeftrip = self.__getlasterror(_res_getafeftrip)
        raise Error(rescode(_res_getafeftrip),_msg_getafeftrip)
      afeidx = array.array("q")
      afeidx.frombytes(afeidx_)
      varidx = array.array("i")
      varidx.frombytes(varidx_)
      val = array.array("d")
      val.frombytes(val_)
      return (afeidx,varidx,val)
    def getafeftrip(self,*args,**kwds):
      """
      Obtains the F matrix in triplet format.
    
      getafeftrip(afeidx,varidx,val)
      getafeftrip() -> (afeidx,varidx,val)
        [afeidx : array(int64)]  Row indices of nonzeros.  
        [val : array(float64)]  Values of nonzero entries.  
        [varidx : array(int32)]  Column indices of nonzeros.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getafeftrip_OOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getafeftrip_OOO_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __putafebarfentry_LiOO_5(self,afeidx,barvaridx,termidx,termweight):
      if termidx is None:
        raise TypeError("Argument termidx may not be None")
      copyback_termidx = False
      if termidx is None:
        termidx_ = None
        memview_termidx = None
      else:
        try:
          memview_termidx = memoryview(termidx)
        except TypeError:
          try:
            _tmparray_termidx = array.array("q",termidx)
          except TypeError:
            raise TypeError("Argument termidx has wrong type") from None
          else:
            memview_termidx = memoryview(_tmparray_termidx)
            copyback_termidx = True
            termidx_ = _tmparray_termidx
        else:
          if memview_termidx.ndim != 1:
            raise TypeError("Argument termidx must be one-dimensional")
          if memview_termidx.format != "q":
            _tmparray_termidx = array.array("q",termidx)
            memview_termidx = memoryview(_tmparray_termidx)
            copyback_termidx = True
            termidx_ = _tmparray_termidx
      if termweight is None:
        raise TypeError("Argument termweight may not be None")
      copyback_termweight = False
      if termweight is None:
        termweight_ = None
        memview_termweight = None
      else:
        try:
          memview_termweight = memoryview(termweight)
        except TypeError:
          try:
            _tmparray_termweight = array.array("d",termweight)
          except TypeError:
            raise TypeError("Argument termweight has wrong type") from None
          else:
            memview_termweight = memoryview(_tmparray_termweight)
            copyback_termweight = True
            termweight_ = _tmparray_termweight
        else:
          if memview_termweight.ndim != 1:
            raise TypeError("Argument termweight must be one-dimensional")
          if memview_termweight.format != "d":
            _tmparray_termweight = array.array("d",termweight)
            memview_termweight = memoryview(_tmparray_termweight)
            copyback_termweight = True
            termweight_ = _tmparray_termweight
      _res_putafebarfentry,_retargs_putafebarfentry = self.__obj.putafebarfentry_LiOO_5(afeidx,barvaridx,memview_termidx,memview_termweight)
      if _res_putafebarfentry != 0:
        _,_msg_putafebarfentry = self.__getlasterror(_res_putafebarfentry)
        raise Error(rescode(_res_putafebarfentry),_msg_putafebarfentry)
    def putafebarfentry(self,*args,**kwds):
      """
      Inputs one entry in barF.
    
      putafebarfentry(afeidx,barvaridx,termidx,termweight)
        [afeidx : int64]  Row index of barF.  
        [barvaridx : int32]  Semidefinite variable index.  
        [termidx : array(int64)]  Element indices in matrix storage.  
        [termweight : array(float64)]  Weights in the weighted sum.  
      """
      return self.__putafebarfentry_LiOO_5(*args,**kwds)
    def __putafebarfentrylist_OOOOOO_7(self,afeidx,barvaridx,numterm,ptrterm,termidx,termweight):
      if afeidx is None:
        raise TypeError("Argument afeidx may not be None")
      copyback_afeidx = False
      if afeidx is None:
        afeidx_ = None
        memview_afeidx = None
      else:
        try:
          memview_afeidx = memoryview(afeidx)
        except TypeError:
          try:
            _tmparray_afeidx = array.array("q",afeidx)
          except TypeError:
            raise TypeError("Argument afeidx has wrong type") from None
          else:
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
        else:
          if memview_afeidx.ndim != 1:
            raise TypeError("Argument afeidx must be one-dimensional")
          if memview_afeidx.format != "q":
            _tmparray_afeidx = array.array("q",afeidx)
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
      if barvaridx is None:
        raise TypeError("Argument barvaridx may not be None")
      copyback_barvaridx = False
      if barvaridx is None:
        barvaridx_ = None
        memview_barvaridx = None
      else:
        try:
          memview_barvaridx = memoryview(barvaridx)
        except TypeError:
          try:
            _tmparray_barvaridx = array.array("i",barvaridx)
          except TypeError:
            raise TypeError("Argument barvaridx has wrong type") from None
          else:
            memview_barvaridx = memoryview(_tmparray_barvaridx)
            copyback_barvaridx = True
            barvaridx_ = _tmparray_barvaridx
        else:
          if memview_barvaridx.ndim != 1:
            raise TypeError("Argument barvaridx must be one-dimensional")
          if memview_barvaridx.format != "i":
            _tmparray_barvaridx = array.array("i",barvaridx)
            memview_barvaridx = memoryview(_tmparray_barvaridx)
            copyback_barvaridx = True
            barvaridx_ = _tmparray_barvaridx
      if numterm is None:
        raise TypeError("Argument numterm may not be None")
      copyback_numterm = False
      if numterm is None:
        numterm_ = None
        memview_numterm = None
      else:
        try:
          memview_numterm = memoryview(numterm)
        except TypeError:
          try:
            _tmparray_numterm = array.array("q",numterm)
          except TypeError:
            raise TypeError("Argument numterm has wrong type") from None
          else:
            memview_numterm = memoryview(_tmparray_numterm)
            copyback_numterm = True
            numterm_ = _tmparray_numterm
        else:
          if memview_numterm.ndim != 1:
            raise TypeError("Argument numterm must be one-dimensional")
          if memview_numterm.format != "q":
            _tmparray_numterm = array.array("q",numterm)
            memview_numterm = memoryview(_tmparray_numterm)
            copyback_numterm = True
            numterm_ = _tmparray_numterm
      if ptrterm is None:
        raise TypeError("Argument ptrterm may not be None")
      copyback_ptrterm = False
      if ptrterm is None:
        ptrterm_ = None
        memview_ptrterm = None
      else:
        try:
          memview_ptrterm = memoryview(ptrterm)
        except TypeError:
          try:
            _tmparray_ptrterm = array.array("q",ptrterm)
          except TypeError:
            raise TypeError("Argument ptrterm has wrong type") from None
          else:
            memview_ptrterm = memoryview(_tmparray_ptrterm)
            copyback_ptrterm = True
            ptrterm_ = _tmparray_ptrterm
        else:
          if memview_ptrterm.ndim != 1:
            raise TypeError("Argument ptrterm must be one-dimensional")
          if memview_ptrterm.format != "q":
            _tmparray_ptrterm = array.array("q",ptrterm)
            memview_ptrterm = memoryview(_tmparray_ptrterm)
            copyback_ptrterm = True
            ptrterm_ = _tmparray_ptrterm
      if termidx is None:
        raise TypeError("Argument termidx may not be None")
      copyback_termidx = False
      if termidx is None:
        termidx_ = None
        memview_termidx = None
      else:
        try:
          memview_termidx = memoryview(termidx)
        except TypeError:
          try:
            _tmparray_termidx = array.array("q",termidx)
          except TypeError:
            raise TypeError("Argument termidx has wrong type") from None
          else:
            memview_termidx = memoryview(_tmparray_termidx)
            copyback_termidx = True
            termidx_ = _tmparray_termidx
        else:
          if memview_termidx.ndim != 1:
            raise TypeError("Argument termidx must be one-dimensional")
          if memview_termidx.format != "q":
            _tmparray_termidx = array.array("q",termidx)
            memview_termidx = memoryview(_tmparray_termidx)
            copyback_termidx = True
            termidx_ = _tmparray_termidx
      if termweight is None:
        raise TypeError("Argument termweight may not be None")
      copyback_termweight = False
      if termweight is None:
        termweight_ = None
        memview_termweight = None
      else:
        try:
          memview_termweight = memoryview(termweight)
        except TypeError:
          try:
            _tmparray_termweight = array.array("d",termweight)
          except TypeError:
            raise TypeError("Argument termweight has wrong type") from None
          else:
            memview_termweight = memoryview(_tmparray_termweight)
            copyback_termweight = True
            termweight_ = _tmparray_termweight
        else:
          if memview_termweight.ndim != 1:
            raise TypeError("Argument termweight must be one-dimensional")
          if memview_termweight.format != "d":
            _tmparray_termweight = array.array("d",termweight)
            memview_termweight = memoryview(_tmparray_termweight)
            copyback_termweight = True
            termweight_ = _tmparray_termweight
      _res_putafebarfentrylist,_retargs_putafebarfentrylist = self.__obj.putafebarfentrylist_OOOOOO_7(memview_afeidx,memview_barvaridx,memview_numterm,memview_ptrterm,memview_termidx,memview_termweight)
      if _res_putafebarfentrylist != 0:
        _,_msg_putafebarfentrylist = self.__getlasterror(_res_putafebarfentrylist)
        raise Error(rescode(_res_putafebarfentrylist),_msg_putafebarfentrylist)
    def putafebarfentrylist(self,*args,**kwds):
      """
      Inputs a list of entries in barF.
    
      putafebarfentrylist(afeidx,
                          barvaridx,
                          numterm,
                          ptrterm,
                          termidx,
                          termweight)
        [afeidx : array(int64)]  Row indexes of barF.  
        [barvaridx : array(int32)]  Semidefinite variable indexes.  
        [numterm : array(int64)]  Number of terms in the weighted sums.  
        [ptrterm : array(int64)]  Pointer to the terms forming each entry.  
        [termidx : array(int64)]  Concatenated element indexes in matrix storage.  
        [termweight : array(float64)]  Concatenated weights in the weighted sum.  
      """
      return self.__putafebarfentrylist_OOOOOO_7(*args,**kwds)
    def __putafebarfrow_LOOOOO_7(self,afeidx,barvaridx,numterm,ptrterm,termidx,termweight):
      if barvaridx is None:
        raise TypeError("Argument barvaridx may not be None")
      copyback_barvaridx = False
      if barvaridx is None:
        barvaridx_ = None
        memview_barvaridx = None
      else:
        try:
          memview_barvaridx = memoryview(barvaridx)
        except TypeError:
          try:
            _tmparray_barvaridx = array.array("i",barvaridx)
          except TypeError:
            raise TypeError("Argument barvaridx has wrong type") from None
          else:
            memview_barvaridx = memoryview(_tmparray_barvaridx)
            copyback_barvaridx = True
            barvaridx_ = _tmparray_barvaridx
        else:
          if memview_barvaridx.ndim != 1:
            raise TypeError("Argument barvaridx must be one-dimensional")
          if memview_barvaridx.format != "i":
            _tmparray_barvaridx = array.array("i",barvaridx)
            memview_barvaridx = memoryview(_tmparray_barvaridx)
            copyback_barvaridx = True
            barvaridx_ = _tmparray_barvaridx
      if numterm is None:
        raise TypeError("Argument numterm may not be None")
      copyback_numterm = False
      if numterm is None:
        numterm_ = None
        memview_numterm = None
      else:
        try:
          memview_numterm = memoryview(numterm)
        except TypeError:
          try:
            _tmparray_numterm = array.array("q",numterm)
          except TypeError:
            raise TypeError("Argument numterm has wrong type") from None
          else:
            memview_numterm = memoryview(_tmparray_numterm)
            copyback_numterm = True
            numterm_ = _tmparray_numterm
        else:
          if memview_numterm.ndim != 1:
            raise TypeError("Argument numterm must be one-dimensional")
          if memview_numterm.format != "q":
            _tmparray_numterm = array.array("q",numterm)
            memview_numterm = memoryview(_tmparray_numterm)
            copyback_numterm = True
            numterm_ = _tmparray_numterm
      if ptrterm is None:
        raise TypeError("Argument ptrterm may not be None")
      copyback_ptrterm = False
      if ptrterm is None:
        ptrterm_ = None
        memview_ptrterm = None
      else:
        try:
          memview_ptrterm = memoryview(ptrterm)
        except TypeError:
          try:
            _tmparray_ptrterm = array.array("q",ptrterm)
          except TypeError:
            raise TypeError("Argument ptrterm has wrong type") from None
          else:
            memview_ptrterm = memoryview(_tmparray_ptrterm)
            copyback_ptrterm = True
            ptrterm_ = _tmparray_ptrterm
        else:
          if memview_ptrterm.ndim != 1:
            raise TypeError("Argument ptrterm must be one-dimensional")
          if memview_ptrterm.format != "q":
            _tmparray_ptrterm = array.array("q",ptrterm)
            memview_ptrterm = memoryview(_tmparray_ptrterm)
            copyback_ptrterm = True
            ptrterm_ = _tmparray_ptrterm
      if termidx is None:
        raise TypeError("Argument termidx may not be None")
      copyback_termidx = False
      if termidx is None:
        termidx_ = None
        memview_termidx = None
      else:
        try:
          memview_termidx = memoryview(termidx)
        except TypeError:
          try:
            _tmparray_termidx = array.array("q",termidx)
          except TypeError:
            raise TypeError("Argument termidx has wrong type") from None
          else:
            memview_termidx = memoryview(_tmparray_termidx)
            copyback_termidx = True
            termidx_ = _tmparray_termidx
        else:
          if memview_termidx.ndim != 1:
            raise TypeError("Argument termidx must be one-dimensional")
          if memview_termidx.format != "q":
            _tmparray_termidx = array.array("q",termidx)
            memview_termidx = memoryview(_tmparray_termidx)
            copyback_termidx = True
            termidx_ = _tmparray_termidx
      if termweight is None:
        raise TypeError("Argument termweight may not be None")
      copyback_termweight = False
      if termweight is None:
        termweight_ = None
        memview_termweight = None
      else:
        try:
          memview_termweight = memoryview(termweight)
        except TypeError:
          try:
            _tmparray_termweight = array.array("d",termweight)
          except TypeError:
            raise TypeError("Argument termweight has wrong type") from None
          else:
            memview_termweight = memoryview(_tmparray_termweight)
            copyback_termweight = True
            termweight_ = _tmparray_termweight
        else:
          if memview_termweight.ndim != 1:
            raise TypeError("Argument termweight must be one-dimensional")
          if memview_termweight.format != "d":
            _tmparray_termweight = array.array("d",termweight)
            memview_termweight = memoryview(_tmparray_termweight)
            copyback_termweight = True
            termweight_ = _tmparray_termweight
      _res_putafebarfrow,_retargs_putafebarfrow = self.__obj.putafebarfrow_LOOOOO_7(afeidx,memview_barvaridx,memview_numterm,memview_ptrterm,memview_termidx,memview_termweight)
      if _res_putafebarfrow != 0:
        _,_msg_putafebarfrow = self.__getlasterror(_res_putafebarfrow)
        raise Error(rescode(_res_putafebarfrow),_msg_putafebarfrow)
    def putafebarfrow(self,*args,**kwds):
      """
      Inputs a row of barF.
    
      putafebarfrow(afeidx,
                    barvaridx,
                    numterm,
                    ptrterm,
                    termidx,
                    termweight)
        [afeidx : int64]  Row index of barF.  
        [barvaridx : array(int32)]  Semidefinite variable indexes.  
        [numterm : array(int64)]  Number of terms in the weighted sums.  
        [ptrterm : array(int64)]  Pointer to the terms forming each entry.  
        [termidx : array(int64)]  Concatenated element indexes in matrix storage.  
        [termweight : array(float64)]  Concatenated weights in the weighted sum.  
      """
      return self.__putafebarfrow_LOOOOO_7(*args,**kwds)
    def __emptyafebarfrow_L_2(self,afeidx):
      _res_emptyafebarfrow,_retargs_emptyafebarfrow = self.__obj.emptyafebarfrow_L_2(afeidx)
      if _res_emptyafebarfrow != 0:
        _,_msg_emptyafebarfrow = self.__getlasterror(_res_emptyafebarfrow)
        raise Error(rescode(_res_emptyafebarfrow),_msg_emptyafebarfrow)
    def emptyafebarfrow(self,*args,**kwds):
      """
      Clears a row in barF
    
      emptyafebarfrow(afeidx)
        [afeidx : int64]  Row index of barF.  
      """
      return self.__emptyafebarfrow_L_2(*args,**kwds)
    def __emptyafebarfrowlist_O_2(self,afeidxlist):
      if afeidxlist is None:
        raise TypeError("Argument afeidxlist may not be None")
      copyback_afeidxlist = False
      if afeidxlist is None:
        afeidxlist_ = None
        memview_afeidxlist = None
      else:
        try:
          memview_afeidxlist = memoryview(afeidxlist)
        except TypeError:
          try:
            _tmparray_afeidxlist = array.array("q",afeidxlist)
          except TypeError:
            raise TypeError("Argument afeidxlist has wrong type") from None
          else:
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
        else:
          if memview_afeidxlist.ndim != 1:
            raise TypeError("Argument afeidxlist must be one-dimensional")
          if memview_afeidxlist.format != "q":
            _tmparray_afeidxlist = array.array("q",afeidxlist)
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
      _res_emptyafebarfrowlist,_retargs_emptyafebarfrowlist = self.__obj.emptyafebarfrowlist_O_2(memview_afeidxlist)
      if _res_emptyafebarfrowlist != 0:
        _,_msg_emptyafebarfrowlist = self.__getlasterror(_res_emptyafebarfrowlist)
        raise Error(rescode(_res_emptyafebarfrowlist),_msg_emptyafebarfrowlist)
    def emptyafebarfrowlist(self,*args,**kwds):
      """
      Clears rows in barF.
    
      emptyafebarfrowlist(afeidxlist)
        [afeidxlist : array(int64)]  Indices of rows in barF to clear.  
      """
      return self.__emptyafebarfrowlist_O_2(*args,**kwds)
    def __putafebarfblocktriplet_OOOOO_6(self,afeidx,barvaridx,subk,subl,valkl):
      if afeidx is None:
        raise TypeError("Argument afeidx may not be None")
      copyback_afeidx = False
      if afeidx is None:
        afeidx_ = None
        memview_afeidx = None
      else:
        try:
          memview_afeidx = memoryview(afeidx)
        except TypeError:
          try:
            _tmparray_afeidx = array.array("q",afeidx)
          except TypeError:
            raise TypeError("Argument afeidx has wrong type") from None
          else:
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
        else:
          if memview_afeidx.ndim != 1:
            raise TypeError("Argument afeidx must be one-dimensional")
          if memview_afeidx.format != "q":
            _tmparray_afeidx = array.array("q",afeidx)
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
      if barvaridx is None:
        raise TypeError("Argument barvaridx may not be None")
      copyback_barvaridx = False
      if barvaridx is None:
        barvaridx_ = None
        memview_barvaridx = None
      else:
        try:
          memview_barvaridx = memoryview(barvaridx)
        except TypeError:
          try:
            _tmparray_barvaridx = array.array("i",barvaridx)
          except TypeError:
            raise TypeError("Argument barvaridx has wrong type") from None
          else:
            memview_barvaridx = memoryview(_tmparray_barvaridx)
            copyback_barvaridx = True
            barvaridx_ = _tmparray_barvaridx
        else:
          if memview_barvaridx.ndim != 1:
            raise TypeError("Argument barvaridx must be one-dimensional")
          if memview_barvaridx.format != "i":
            _tmparray_barvaridx = array.array("i",barvaridx)
            memview_barvaridx = memoryview(_tmparray_barvaridx)
            copyback_barvaridx = True
            barvaridx_ = _tmparray_barvaridx
      if subk is None:
        raise TypeError("Argument subk may not be None")
      copyback_subk = False
      if subk is None:
        subk_ = None
        memview_subk = None
      else:
        try:
          memview_subk = memoryview(subk)
        except TypeError:
          try:
            _tmparray_subk = array.array("i",subk)
          except TypeError:
            raise TypeError("Argument subk has wrong type") from None
          else:
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
        else:
          if memview_subk.ndim != 1:
            raise TypeError("Argument subk must be one-dimensional")
          if memview_subk.format != "i":
            _tmparray_subk = array.array("i",subk)
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
      if subl is None:
        raise TypeError("Argument subl may not be None")
      copyback_subl = False
      if subl is None:
        subl_ = None
        memview_subl = None
      else:
        try:
          memview_subl = memoryview(subl)
        except TypeError:
          try:
            _tmparray_subl = array.array("i",subl)
          except TypeError:
            raise TypeError("Argument subl has wrong type") from None
          else:
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
        else:
          if memview_subl.ndim != 1:
            raise TypeError("Argument subl must be one-dimensional")
          if memview_subl.format != "i":
            _tmparray_subl = array.array("i",subl)
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
      if valkl is None:
        raise TypeError("Argument valkl may not be None")
      copyback_valkl = False
      if valkl is None:
        valkl_ = None
        memview_valkl = None
      else:
        try:
          memview_valkl = memoryview(valkl)
        except TypeError:
          try:
            _tmparray_valkl = array.array("d",valkl)
          except TypeError:
            raise TypeError("Argument valkl has wrong type") from None
          else:
            memview_valkl = memoryview(_tmparray_valkl)
            copyback_valkl = True
            valkl_ = _tmparray_valkl
        else:
          if memview_valkl.ndim != 1:
            raise TypeError("Argument valkl must be one-dimensional")
          if memview_valkl.format != "d":
            _tmparray_valkl = array.array("d",valkl)
            memview_valkl = memoryview(_tmparray_valkl)
            copyback_valkl = True
            valkl_ = _tmparray_valkl
      _res_putafebarfblocktriplet,_retargs_putafebarfblocktriplet = self.__obj.putafebarfblocktriplet_OOOOO_6(memview_afeidx,memview_barvaridx,memview_subk,memview_subl,memview_valkl)
      if _res_putafebarfblocktriplet != 0:
        _,_msg_putafebarfblocktriplet = self.__getlasterror(_res_putafebarfblocktriplet)
        raise Error(rescode(_res_putafebarfblocktriplet),_msg_putafebarfblocktriplet)
    def putafebarfblocktriplet(self,*args,**kwds):
      """
      Inputs barF in block triplet form.
    
      putafebarfblocktriplet(afeidx,barvaridx,subk,subl,valkl)
        [afeidx : array(int64)]  Constraint index.  
        [barvaridx : array(int32)]  Symmetric matrix variable index.  
        [subk : array(int32)]  Block row index.  
        [subl : array(int32)]  Block column index.  
        [valkl : array(float64)]  The numerical value associated with each block triplet.  
      """
      return self.__putafebarfblocktriplet_OOOOO_6(*args,**kwds)
    def __getafebarfnumblocktriplets__1(self):
      _res_getafebarfnumblocktriplets,_retargs_getafebarfnumblocktriplets = self.__obj.getafebarfnumblocktriplets__1()
      if _res_getafebarfnumblocktriplets != 0:
        _,_msg_getafebarfnumblocktriplets = self.__getlasterror(_res_getafebarfnumblocktriplets)
        raise Error(rescode(_res_getafebarfnumblocktriplets),_msg_getafebarfnumblocktriplets)
      else:
        (numtrip) = _retargs_getafebarfnumblocktriplets
      return (numtrip)
    def getafebarfnumblocktriplets(self,*args,**kwds):
      """
      Obtains an upper bound on the number of elements in the block triplet form of barf.
    
      getafebarfnumblocktriplets() -> (numtrip)
        [numtrip : int64]  An upper bound on the number of elements in the block triplet form of barf.  
      """
      return self.__getafebarfnumblocktriplets__1(*args,**kwds)
    def __getafebarfblocktriplet_OOOOO_6(self,afeidx,barvaridx,subk,subl,valkl):
      if afeidx is None:
        raise TypeError("Argument afeidx may not be None")
      copyback_afeidx = False
      if afeidx is None:
        afeidx_ = None
        memview_afeidx = None
      else:
        try:
          memview_afeidx = memoryview(afeidx)
        except TypeError:
          try:
            _tmparray_afeidx = array.array("q",[0 for _ in range(len(afeidx))])
          except TypeError:
            raise TypeError("Argument afeidx has wrong type") from None
          else:
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
        else:
          if memview_afeidx.ndim != 1:
            raise TypeError("Argument afeidx must be one-dimensional")
          if memview_afeidx.format != "q":
            _tmparray_afeidx = array.array("q",afeidx)
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
      if barvaridx is None:
        raise TypeError("Argument barvaridx may not be None")
      copyback_barvaridx = False
      if barvaridx is None:
        barvaridx_ = None
        memview_barvaridx = None
      else:
        try:
          memview_barvaridx = memoryview(barvaridx)
        except TypeError:
          try:
            _tmparray_barvaridx = array.array("i",[0 for _ in range(len(barvaridx))])
          except TypeError:
            raise TypeError("Argument barvaridx has wrong type") from None
          else:
            memview_barvaridx = memoryview(_tmparray_barvaridx)
            copyback_barvaridx = True
            barvaridx_ = _tmparray_barvaridx
        else:
          if memview_barvaridx.ndim != 1:
            raise TypeError("Argument barvaridx must be one-dimensional")
          if memview_barvaridx.format != "i":
            _tmparray_barvaridx = array.array("i",barvaridx)
            memview_barvaridx = memoryview(_tmparray_barvaridx)
            copyback_barvaridx = True
            barvaridx_ = _tmparray_barvaridx
      if subk is None:
        raise TypeError("Argument subk may not be None")
      copyback_subk = False
      if subk is None:
        subk_ = None
        memview_subk = None
      else:
        try:
          memview_subk = memoryview(subk)
        except TypeError:
          try:
            _tmparray_subk = array.array("i",[0 for _ in range(len(subk))])
          except TypeError:
            raise TypeError("Argument subk has wrong type") from None
          else:
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
        else:
          if memview_subk.ndim != 1:
            raise TypeError("Argument subk must be one-dimensional")
          if memview_subk.format != "i":
            _tmparray_subk = array.array("i",subk)
            memview_subk = memoryview(_tmparray_subk)
            copyback_subk = True
            subk_ = _tmparray_subk
      if subl is None:
        raise TypeError("Argument subl may not be None")
      copyback_subl = False
      if subl is None:
        subl_ = None
        memview_subl = None
      else:
        try:
          memview_subl = memoryview(subl)
        except TypeError:
          try:
            _tmparray_subl = array.array("i",[0 for _ in range(len(subl))])
          except TypeError:
            raise TypeError("Argument subl has wrong type") from None
          else:
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
        else:
          if memview_subl.ndim != 1:
            raise TypeError("Argument subl must be one-dimensional")
          if memview_subl.format != "i":
            _tmparray_subl = array.array("i",subl)
            memview_subl = memoryview(_tmparray_subl)
            copyback_subl = True
            subl_ = _tmparray_subl
      if valkl is None:
        raise TypeError("Argument valkl may not be None")
      copyback_valkl = False
      if valkl is None:
        valkl_ = None
        memview_valkl = None
      else:
        try:
          memview_valkl = memoryview(valkl)
        except TypeError:
          try:
            _tmparray_valkl = array.array("d",[0 for _ in range(len(valkl))])
          except TypeError:
            raise TypeError("Argument valkl has wrong type") from None
          else:
            memview_valkl = memoryview(_tmparray_valkl)
            copyback_valkl = True
            valkl_ = _tmparray_valkl
        else:
          if memview_valkl.ndim != 1:
            raise TypeError("Argument valkl must be one-dimensional")
          if memview_valkl.format != "d":
            _tmparray_valkl = array.array("d",valkl)
            memview_valkl = memoryview(_tmparray_valkl)
            copyback_valkl = True
            valkl_ = _tmparray_valkl
      _res_getafebarfblocktriplet,_retargs_getafebarfblocktriplet = self.__obj.getafebarfblocktriplet_OOOOO_6(memview_afeidx,memview_barvaridx,memview_subk,memview_subl,memview_valkl)
      if _res_getafebarfblocktriplet != 0:
        _,_msg_getafebarfblocktriplet = self.__getlasterror(_res_getafebarfblocktriplet)
        raise Error(rescode(_res_getafebarfblocktriplet),_msg_getafebarfblocktriplet)
      else:
        (numtrip) = _retargs_getafebarfblocktriplet
      if copyback_afeidx:
        for __tmp_1088 in range(len(afeidx)): afeidx[__tmp_1088] = afeidx_[__tmp_1088]
      if copyback_barvaridx:
        for __tmp_1089 in range(len(barvaridx)): barvaridx[__tmp_1089] = barvaridx_[__tmp_1089]
      if copyback_subk:
        for __tmp_1090 in range(len(subk)): subk[__tmp_1090] = subk_[__tmp_1090]
      if copyback_subl:
        for __tmp_1091 in range(len(subl)): subl[__tmp_1091] = subl_[__tmp_1091]
      if copyback_valkl:
        for __tmp_1092 in range(len(valkl)): valkl[__tmp_1092] = valkl_[__tmp_1092]
      return (numtrip)
    def __getafebarfblocktriplet_OOOOO_1(self):
      afeidx_ = bytearray(0)
      barvaridx_ = bytearray(0)
      subk_ = bytearray(0)
      subl_ = bytearray(0)
      valkl_ = bytearray(0)
      _res_getafebarfblocktriplet,_retargs_getafebarfblocktriplet = self.__obj.getafebarfblocktriplet_OOOOO_1(afeidx_,barvaridx_,subk_,subl_,valkl_)
      if _res_getafebarfblocktriplet != 0:
        _,_msg_getafebarfblocktriplet = self.__getlasterror(_res_getafebarfblocktriplet)
        raise Error(rescode(_res_getafebarfblocktriplet),_msg_getafebarfblocktriplet)
      else:
        (numtrip) = _retargs_getafebarfblocktriplet
      afeidx = array.array("q")
      afeidx.frombytes(afeidx_)
      barvaridx = array.array("i")
      barvaridx.frombytes(barvaridx_)
      subk = array.array("i")
      subk.frombytes(subk_)
      subl = array.array("i")
      subl.frombytes(subl_)
      valkl = array.array("d")
      valkl.frombytes(valkl_)
      return (numtrip,afeidx,barvaridx,subk,subl,valkl)
    def getafebarfblocktriplet(self,*args,**kwds):
      """
      Obtains barF in block triplet form.
    
      getafebarfblocktriplet(afeidx,barvaridx,subk,subl,valkl) -> (numtrip)
      getafebarfblocktriplet() -> 
                            (numtrip,
                             afeidx,
                             barvaridx,
                             subk,
                             subl,
                             valkl)
        [afeidx : array(int64)]  Constraint index.  
        [barvaridx : array(int32)]  Symmetric matrix variable index.  
        [numtrip : int64]  Number of elements in the block triplet form.  
        [subk : array(int32)]  Block row index.  
        [subl : array(int32)]  Block column index.  
        [valkl : array(float64)]  The numerical value associated with each block triplet.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__getafebarfblocktriplet_OOOOO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getafebarfblocktriplet_OOOOO_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getafebarfnumrowentries_L_2(self,afeidx):
      _res_getafebarfnumrowentries,_retargs_getafebarfnumrowentries = self.__obj.getafebarfnumrowentries_L_2(afeidx)
      if _res_getafebarfnumrowentries != 0:
        _,_msg_getafebarfnumrowentries = self.__getlasterror(_res_getafebarfnumrowentries)
        raise Error(rescode(_res_getafebarfnumrowentries),_msg_getafebarfnumrowentries)
      else:
        (numentr) = _retargs_getafebarfnumrowentries
      return (numentr)
    def getafebarfnumrowentries(self,*args,**kwds):
      """
      Obtains the number of nonzero entries in a row of barF.
    
      getafebarfnumrowentries(afeidx) -> (numentr)
        [afeidx : int64]  Row index of barF.  
        [numentr : int32]  Number of nonzero entries in a row of barF.  
      """
      return self.__getafebarfnumrowentries_L_2(*args,**kwds)
    def __getafebarfrowinfo_L_2(self,afeidx):
      _res_getafebarfrowinfo,_retargs_getafebarfrowinfo = self.__obj.getafebarfrowinfo_L_2(afeidx)
      if _res_getafebarfrowinfo != 0:
        _,_msg_getafebarfrowinfo = self.__getlasterror(_res_getafebarfrowinfo)
        raise Error(rescode(_res_getafebarfrowinfo),_msg_getafebarfrowinfo)
      else:
        (numentr,numterm) = _retargs_getafebarfrowinfo
      return (numentr,numterm)
    def getafebarfrowinfo(self,*args,**kwds):
      """
      Obtains information about one row of barF.
    
      getafebarfrowinfo(afeidx) -> (numentr,numterm)
        [afeidx : int64]  Row index of barF.  
        [numentr : int32]  Number of nonzero entries in a row of barF.  
        [numterm : int64]  Number of terms in the weighted sums representation of the row of barF.  
      """
      return self.__getafebarfrowinfo_L_2(*args,**kwds)
    def __getafebarfrow_LOOOOO_7(self,afeidx,barvaridx,ptrterm,numterm,termidx,termweight):
      if barvaridx is None:
        raise TypeError("Argument barvaridx may not be None")
      copyback_barvaridx = False
      if barvaridx is None:
        barvaridx_ = None
        memview_barvaridx = None
      else:
        try:
          memview_barvaridx = memoryview(barvaridx)
        except TypeError:
          try:
            _tmparray_barvaridx = array.array("i",[0 for _ in range(len(barvaridx))])
          except TypeError:
            raise TypeError("Argument barvaridx has wrong type") from None
          else:
            memview_barvaridx = memoryview(_tmparray_barvaridx)
            copyback_barvaridx = True
            barvaridx_ = _tmparray_barvaridx
        else:
          if memview_barvaridx.ndim != 1:
            raise TypeError("Argument barvaridx must be one-dimensional")
          if memview_barvaridx.format != "i":
            _tmparray_barvaridx = array.array("i",barvaridx)
            memview_barvaridx = memoryview(_tmparray_barvaridx)
            copyback_barvaridx = True
            barvaridx_ = _tmparray_barvaridx
      if ptrterm is None:
        raise TypeError("Argument ptrterm may not be None")
      copyback_ptrterm = False
      if ptrterm is None:
        ptrterm_ = None
        memview_ptrterm = None
      else:
        try:
          memview_ptrterm = memoryview(ptrterm)
        except TypeError:
          try:
            _tmparray_ptrterm = array.array("q",[0 for _ in range(len(ptrterm))])
          except TypeError:
            raise TypeError("Argument ptrterm has wrong type") from None
          else:
            memview_ptrterm = memoryview(_tmparray_ptrterm)
            copyback_ptrterm = True
            ptrterm_ = _tmparray_ptrterm
        else:
          if memview_ptrterm.ndim != 1:
            raise TypeError("Argument ptrterm must be one-dimensional")
          if memview_ptrterm.format != "q":
            _tmparray_ptrterm = array.array("q",ptrterm)
            memview_ptrterm = memoryview(_tmparray_ptrterm)
            copyback_ptrterm = True
            ptrterm_ = _tmparray_ptrterm
      if numterm is None:
        raise TypeError("Argument numterm may not be None")
      copyback_numterm = False
      if numterm is None:
        numterm_ = None
        memview_numterm = None
      else:
        try:
          memview_numterm = memoryview(numterm)
        except TypeError:
          try:
            _tmparray_numterm = array.array("q",[0 for _ in range(len(numterm))])
          except TypeError:
            raise TypeError("Argument numterm has wrong type") from None
          else:
            memview_numterm = memoryview(_tmparray_numterm)
            copyback_numterm = True
            numterm_ = _tmparray_numterm
        else:
          if memview_numterm.ndim != 1:
            raise TypeError("Argument numterm must be one-dimensional")
          if memview_numterm.format != "q":
            _tmparray_numterm = array.array("q",numterm)
            memview_numterm = memoryview(_tmparray_numterm)
            copyback_numterm = True
            numterm_ = _tmparray_numterm
      if termidx is None:
        raise TypeError("Argument termidx may not be None")
      copyback_termidx = False
      if termidx is None:
        termidx_ = None
        memview_termidx = None
      else:
        try:
          memview_termidx = memoryview(termidx)
        except TypeError:
          try:
            _tmparray_termidx = array.array("q",[0 for _ in range(len(termidx))])
          except TypeError:
            raise TypeError("Argument termidx has wrong type") from None
          else:
            memview_termidx = memoryview(_tmparray_termidx)
            copyback_termidx = True
            termidx_ = _tmparray_termidx
        else:
          if memview_termidx.ndim != 1:
            raise TypeError("Argument termidx must be one-dimensional")
          if memview_termidx.format != "q":
            _tmparray_termidx = array.array("q",termidx)
            memview_termidx = memoryview(_tmparray_termidx)
            copyback_termidx = True
            termidx_ = _tmparray_termidx
      if termweight is None:
        raise TypeError("Argument termweight may not be None")
      copyback_termweight = False
      if termweight is None:
        termweight_ = None
        memview_termweight = None
      else:
        try:
          memview_termweight = memoryview(termweight)
        except TypeError:
          try:
            _tmparray_termweight = array.array("d",[0 for _ in range(len(termweight))])
          except TypeError:
            raise TypeError("Argument termweight has wrong type") from None
          else:
            memview_termweight = memoryview(_tmparray_termweight)
            copyback_termweight = True
            termweight_ = _tmparray_termweight
        else:
          if memview_termweight.ndim != 1:
            raise TypeError("Argument termweight must be one-dimensional")
          if memview_termweight.format != "d":
            _tmparray_termweight = array.array("d",termweight)
            memview_termweight = memoryview(_tmparray_termweight)
            copyback_termweight = True
            termweight_ = _tmparray_termweight
      _res_getafebarfrow,_retargs_getafebarfrow = self.__obj.getafebarfrow_LOOOOO_7(afeidx,memview_barvaridx,memview_ptrterm,memview_numterm,memview_termidx,memview_termweight)
      if _res_getafebarfrow != 0:
        _,_msg_getafebarfrow = self.__getlasterror(_res_getafebarfrow)
        raise Error(rescode(_res_getafebarfrow),_msg_getafebarfrow)
      if copyback_barvaridx:
        for __tmp_1103 in range(len(barvaridx)): barvaridx[__tmp_1103] = barvaridx_[__tmp_1103]
      if copyback_ptrterm:
        for __tmp_1107 in range(len(ptrterm)): ptrterm[__tmp_1107] = ptrterm_[__tmp_1107]
      if copyback_numterm:
        for __tmp_1111 in range(len(numterm)): numterm[__tmp_1111] = numterm_[__tmp_1111]
      if copyback_termidx:
        for __tmp_1115 in range(len(termidx)): termidx[__tmp_1115] = termidx_[__tmp_1115]
      if copyback_termweight:
        for __tmp_1119 in range(len(termweight)): termweight[__tmp_1119] = termweight_[__tmp_1119]
    def __getafebarfrow_LOOOOO_2(self,afeidx):
      barvaridx_ = bytearray(0)
      ptrterm_ = bytearray(0)
      numterm_ = bytearray(0)
      termidx_ = bytearray(0)
      termweight_ = bytearray(0)
      _res_getafebarfrow,_retargs_getafebarfrow = self.__obj.getafebarfrow_LOOOOO_2(afeidx,barvaridx_,ptrterm_,numterm_,termidx_,termweight_)
      if _res_getafebarfrow != 0:
        _,_msg_getafebarfrow = self.__getlasterror(_res_getafebarfrow)
        raise Error(rescode(_res_getafebarfrow),_msg_getafebarfrow)
      barvaridx = array.array("i")
      barvaridx.frombytes(barvaridx_)
      ptrterm = array.array("q")
      ptrterm.frombytes(ptrterm_)
      numterm = array.array("q")
      numterm.frombytes(numterm_)
      termidx = array.array("q")
      termidx.frombytes(termidx_)
      termweight = array.array("d")
      termweight.frombytes(termweight_)
      return (barvaridx,ptrterm,numterm,termidx,termweight)
    def getafebarfrow(self,*args,**kwds):
      """
      Obtains nonzero entries in one row of barF.
    
      getafebarfrow(afeidx,
                    barvaridx,
                    ptrterm,
                    numterm,
                    termidx,
                    termweight)
      getafebarfrow(afeidx) -> 
                   (barvaridx,
                    ptrterm,
                    numterm,
                    termidx,
                    termweight)
        [afeidx : int64]  Row index of barF.  
        [barvaridx : array(int32)]  Semidefinite variable indices.  
        [numterm : array(int64)]  Number of terms in each entry.  
        [ptrterm : array(int64)]  Pointers to the description of entries.  
        [termidx : array(int64)]  Indices of semidefinite matrices from E.  
        [termweight : array(float64)]  Weights appearing in the weighted sum representation.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 7: return self.__getafebarfrow_LOOOOO_7(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getafebarfrow_LOOOOO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __putafeg_Ld_3(self,afeidx,g):
      _res_putafeg,_retargs_putafeg = self.__obj.putafeg_Ld_3(afeidx,g)
      if _res_putafeg != 0:
        _,_msg_putafeg = self.__getlasterror(_res_putafeg)
        raise Error(rescode(_res_putafeg),_msg_putafeg)
    def putafeg(self,*args,**kwds):
      """
      Replaces one element in the g vector in the affine expressions.
    
      putafeg(afeidx,g)
        [afeidx : int64]  Row index.  
        [g : float64]  New value for the element of g.  
      """
      return self.__putafeg_Ld_3(*args,**kwds)
    def __putafeglist_OO_3(self,afeidx,g):
      if afeidx is None:
        raise TypeError("Argument afeidx may not be None")
      copyback_afeidx = False
      if afeidx is None:
        afeidx_ = None
        memview_afeidx = None
      else:
        try:
          memview_afeidx = memoryview(afeidx)
        except TypeError:
          try:
            _tmparray_afeidx = array.array("q",afeidx)
          except TypeError:
            raise TypeError("Argument afeidx has wrong type") from None
          else:
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
        else:
          if memview_afeidx.ndim != 1:
            raise TypeError("Argument afeidx must be one-dimensional")
          if memview_afeidx.format != "q":
            _tmparray_afeidx = array.array("q",afeidx)
            memview_afeidx = memoryview(_tmparray_afeidx)
            copyback_afeidx = True
            afeidx_ = _tmparray_afeidx
      if g is None:
        raise TypeError("Argument g may not be None")
      copyback_g = False
      if g is None:
        g_ = None
        memview_g = None
      else:
        try:
          memview_g = memoryview(g)
        except TypeError:
          try:
            _tmparray_g = array.array("d",g)
          except TypeError:
            raise TypeError("Argument g has wrong type") from None
          else:
            memview_g = memoryview(_tmparray_g)
            copyback_g = True
            g_ = _tmparray_g
        else:
          if memview_g.ndim != 1:
            raise TypeError("Argument g must be one-dimensional")
          if memview_g.format != "d":
            _tmparray_g = array.array("d",g)
            memview_g = memoryview(_tmparray_g)
            copyback_g = True
            g_ = _tmparray_g
      _res_putafeglist,_retargs_putafeglist = self.__obj.putafeglist_OO_3(memview_afeidx,memview_g)
      if _res_putafeglist != 0:
        _,_msg_putafeglist = self.__getlasterror(_res_putafeglist)
        raise Error(rescode(_res_putafeglist),_msg_putafeglist)
    def putafeglist(self,*args,**kwds):
      """
      Replaces a list of elements in the g vector in the affine expressions.
    
      putafeglist(afeidx,g)
        [afeidx : array(int64)]  Indices of entries in g.  
        [g : array(float64)]  New values for the elements of g.  
      """
      return self.__putafeglist_OO_3(*args,**kwds)
    def __getafeg_L_2(self,afeidx):
      _res_getafeg,_retargs_getafeg = self.__obj.getafeg_L_2(afeidx)
      if _res_getafeg != 0:
        _,_msg_getafeg = self.__getlasterror(_res_getafeg)
        raise Error(rescode(_res_getafeg),_msg_getafeg)
      else:
        (g) = _retargs_getafeg
      return (g)
    def getafeg(self,*args,**kwds):
      """
      Obtains a single coefficient in g.
    
      getafeg(afeidx) -> (g)
        [afeidx : int64]  Element index.  
        [g : float64]  The entry in g.  
      """
      return self.__getafeg_L_2(*args,**kwds)
    def __getafegslice_LLO_4(self,first,last,g):
      copyback_g = False
      if g is None:
        g_ = None
        memview_g = None
      else:
        try:
          memview_g = memoryview(g)
        except TypeError:
          try:
            _tmparray_g = array.array("d",[0 for _ in range(len(g))])
          except TypeError:
            raise TypeError("Argument g has wrong type") from None
          else:
            memview_g = memoryview(_tmparray_g)
            copyback_g = True
            g_ = _tmparray_g
        else:
          if memview_g.ndim != 1:
            raise TypeError("Argument g must be one-dimensional")
          if memview_g.format != "d":
            _tmparray_g = array.array("d",g)
            memview_g = memoryview(_tmparray_g)
            copyback_g = True
            g_ = _tmparray_g
      _res_getafegslice,_retargs_getafegslice = self.__obj.getafegslice_LLO_4(first,last,memview_g)
      if _res_getafegslice != 0:
        _,_msg_getafegslice = self.__getlasterror(_res_getafegslice)
        raise Error(rescode(_res_getafegslice),_msg_getafegslice)
      if copyback_g:
        for __tmp_1144 in range(len(g)): g[__tmp_1144] = g_[__tmp_1144]
    def __getafegslice_LLO_3(self,first,last):
      g_ = bytearray(0)
      _res_getafegslice,_retargs_getafegslice = self.__obj.getafegslice_LLO_3(first,last,g_)
      if _res_getafegslice != 0:
        _,_msg_getafegslice = self.__getlasterror(_res_getafegslice)
        raise Error(rescode(_res_getafegslice),_msg_getafegslice)
      g = array.array("d")
      g.frombytes(g_)
      return (g)
    def getafegslice(self,*args,**kwds):
      """
      Obtains a sequence of coefficients from the vector g.
    
      getafegslice(first,last,g)
      getafegslice(first,last) -> (g)
        [first : int64]  First index in the sequence.  
        [g : array(float64)]  The slice of g as a dense vector.  
        [last : int64]  Last index plus 1 in the sequence.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getafegslice_LLO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 3: return self.__getafegslice_LLO_3(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __putafegslice_LLO_4(self,first,last,slice):
      if slice is None:
        raise TypeError("Argument slice may not be None")
      copyback_slice = False
      if slice is None:
        slice_ = None
        memview_slice = None
      else:
        try:
          memview_slice = memoryview(slice)
        except TypeError:
          try:
            _tmparray_slice = array.array("d",slice)
          except TypeError:
            raise TypeError("Argument slice has wrong type") from None
          else:
            memview_slice = memoryview(_tmparray_slice)
            copyback_slice = True
            slice_ = _tmparray_slice
        else:
          if memview_slice.ndim != 1:
            raise TypeError("Argument slice must be one-dimensional")
          if memview_slice.format != "d":
            _tmparray_slice = array.array("d",slice)
            memview_slice = memoryview(_tmparray_slice)
            copyback_slice = True
            slice_ = _tmparray_slice
      _res_putafegslice,_retargs_putafegslice = self.__obj.putafegslice_LLO_4(first,last,memview_slice)
      if _res_putafegslice != 0:
        _,_msg_putafegslice = self.__getlasterror(_res_putafegslice)
        raise Error(rescode(_res_putafegslice),_msg_putafegslice)
    def putafegslice(self,*args,**kwds):
      """
      Modifies a slice of the vector g.
    
      putafegslice(first,last,slice)
        [first : int64]  First index in the sequence.  
        [last : int64]  Last index plus 1 in the sequence.  
        [slice : array(float64)]  The slice of g as a dense vector.  
      """
      return self.__putafegslice_LLO_4(*args,**kwds)
    def __putmaxnumdjc_L_2(self,maxnumdjc):
      _res_putmaxnumdjc,_retargs_putmaxnumdjc = self.__obj.putmaxnumdjc_L_2(maxnumdjc)
      if _res_putmaxnumdjc != 0:
        _,_msg_putmaxnumdjc = self.__getlasterror(_res_putmaxnumdjc)
        raise Error(rescode(_res_putmaxnumdjc),_msg_putmaxnumdjc)
    def putmaxnumdjc(self,*args,**kwds):
      """
      Sets the number of preallocated disjunctive constraints.
    
      putmaxnumdjc(maxnumdjc)
        [maxnumdjc : int64]  Number of preallocated disjunctive constraints in the task.  
      """
      return self.__putmaxnumdjc_L_2(*args,**kwds)
    def __getnumdjc__1(self):
      _res_getnumdjc,_retargs_getnumdjc = self.__obj.getnumdjc__1()
      if _res_getnumdjc != 0:
        _,_msg_getnumdjc = self.__getlasterror(_res_getnumdjc)
        raise Error(rescode(_res_getnumdjc),_msg_getnumdjc)
      else:
        (num) = _retargs_getnumdjc
      return (num)
    def getnumdjc(self,*args,**kwds):
      """
      Obtains the number of disjunctive constraints.
    
      getnumdjc() -> (num)
        [num : int64]  The number of disjunctive constraints.  
      """
      return self.__getnumdjc__1(*args,**kwds)
    def __getdjcnumdomain_L_2(self,djcidx):
      _res_getdjcnumdomain,_retargs_getdjcnumdomain = self.__obj.getdjcnumdomain_L_2(djcidx)
      if _res_getdjcnumdomain != 0:
        _,_msg_getdjcnumdomain = self.__getlasterror(_res_getdjcnumdomain)
        raise Error(rescode(_res_getdjcnumdomain),_msg_getdjcnumdomain)
      else:
        (numdomain) = _retargs_getdjcnumdomain
      return (numdomain)
    def getdjcnumdomain(self,*args,**kwds):
      """
      Obtains the number of domains in the disjunctive constraint.
    
      getdjcnumdomain(djcidx) -> (numdomain)
        [djcidx : int64]  Index of the disjunctive constraint.  
        [numdomain : int64]  Number of domains in the disjunctive constraint.  
      """
      return self.__getdjcnumdomain_L_2(*args,**kwds)
    def __getdjcnumdomaintot__1(self):
      _res_getdjcnumdomaintot,_retargs_getdjcnumdomaintot = self.__obj.getdjcnumdomaintot__1()
      if _res_getdjcnumdomaintot != 0:
        _,_msg_getdjcnumdomaintot = self.__getlasterror(_res_getdjcnumdomaintot)
        raise Error(rescode(_res_getdjcnumdomaintot),_msg_getdjcnumdomaintot)
      else:
        (numdomaintot) = _retargs_getdjcnumdomaintot
      return (numdomaintot)
    def getdjcnumdomaintot(self,*args,**kwds):
      """
      Obtains the number of domains in all disjunctive constraints.
    
      getdjcnumdomaintot() -> (numdomaintot)
        [numdomaintot : int64]  Number of domains in all disjunctive constraints.  
      """
      return self.__getdjcnumdomaintot__1(*args,**kwds)
    def __getdjcnumafe_L_2(self,djcidx):
      _res_getdjcnumafe,_retargs_getdjcnumafe = self.__obj.getdjcnumafe_L_2(djcidx)
      if _res_getdjcnumafe != 0:
        _,_msg_getdjcnumafe = self.__getlasterror(_res_getdjcnumafe)
        raise Error(rescode(_res_getdjcnumafe),_msg_getdjcnumafe)
      else:
        (numafe) = _retargs_getdjcnumafe
      return (numafe)
    def getdjcnumafe(self,*args,**kwds):
      """
      Obtains the number of affine expressions in the disjunctive constraint.
    
      getdjcnumafe(djcidx) -> (numafe)
        [djcidx : int64]  Index of the disjunctive constraint.  
        [numafe : int64]  Number of affine expressions in the disjunctive constraint.  
      """
      return self.__getdjcnumafe_L_2(*args,**kwds)
    def __getdjcnumafetot__1(self):
      _res_getdjcnumafetot,_retargs_getdjcnumafetot = self.__obj.getdjcnumafetot__1()
      if _res_getdjcnumafetot != 0:
        _,_msg_getdjcnumafetot = self.__getlasterror(_res_getdjcnumafetot)
        raise Error(rescode(_res_getdjcnumafetot),_msg_getdjcnumafetot)
      else:
        (numafetot) = _retargs_getdjcnumafetot
      return (numafetot)
    def getdjcnumafetot(self,*args,**kwds):
      """
      Obtains the number of affine expressions in all disjunctive constraints.
    
      getdjcnumafetot() -> (numafetot)
        [numafetot : int64]  Number of affine expressions in all disjunctive constraints.  
      """
      return self.__getdjcnumafetot__1(*args,**kwds)
    def __getdjcnumterm_L_2(self,djcidx):
      _res_getdjcnumterm,_retargs_getdjcnumterm = self.__obj.getdjcnumterm_L_2(djcidx)
      if _res_getdjcnumterm != 0:
        _,_msg_getdjcnumterm = self.__getlasterror(_res_getdjcnumterm)
        raise Error(rescode(_res_getdjcnumterm),_msg_getdjcnumterm)
      else:
        (numterm) = _retargs_getdjcnumterm
      return (numterm)
    def getdjcnumterm(self,*args,**kwds):
      """
      Obtains the number terms in the disjunctive constraint.
    
      getdjcnumterm(djcidx) -> (numterm)
        [djcidx : int64]  Index of the disjunctive constraint.  
        [numterm : int64]  Number of terms in the disjunctive constraint.  
      """
      return self.__getdjcnumterm_L_2(*args,**kwds)
    def __getdjcnumtermtot__1(self):
      _res_getdjcnumtermtot,_retargs_getdjcnumtermtot = self.__obj.getdjcnumtermtot__1()
      if _res_getdjcnumtermtot != 0:
        _,_msg_getdjcnumtermtot = self.__getlasterror(_res_getdjcnumtermtot)
        raise Error(rescode(_res_getdjcnumtermtot),_msg_getdjcnumtermtot)
      else:
        (numtermtot) = _retargs_getdjcnumtermtot
      return (numtermtot)
    def getdjcnumtermtot(self,*args,**kwds):
      """
      Obtains the number of terms in all disjunctive constraints.
    
      getdjcnumtermtot() -> (numtermtot)
        [numtermtot : int64]  Total number of terms in all disjunctive constraints.  
      """
      return self.__getdjcnumtermtot__1(*args,**kwds)
    def __putmaxnumacc_L_2(self,maxnumacc):
      _res_putmaxnumacc,_retargs_putmaxnumacc = self.__obj.putmaxnumacc_L_2(maxnumacc)
      if _res_putmaxnumacc != 0:
        _,_msg_putmaxnumacc = self.__getlasterror(_res_putmaxnumacc)
        raise Error(rescode(_res_putmaxnumacc),_msg_putmaxnumacc)
    def putmaxnumacc(self,*args,**kwds):
      """
      Sets the number of preallocated affine conic constraints.
    
      putmaxnumacc(maxnumacc)
        [maxnumacc : int64]  Number of preallocated affine conic constraints.  
      """
      return self.__putmaxnumacc_L_2(*args,**kwds)
    def __getnumacc__1(self):
      _res_getnumacc,_retargs_getnumacc = self.__obj.getnumacc__1()
      if _res_getnumacc != 0:
        _,_msg_getnumacc = self.__getlasterror(_res_getnumacc)
        raise Error(rescode(_res_getnumacc),_msg_getnumacc)
      else:
        (num) = _retargs_getnumacc
      return (num)
    def getnumacc(self,*args,**kwds):
      """
      Obtains the number of affine conic constraints.
    
      getnumacc() -> (num)
        [num : int64]  The number of affine conic constraints.  
      """
      return self.__getnumacc__1(*args,**kwds)
    def __appendacc_LOO_4(self,domidx,afeidxlist,b):
      if afeidxlist is None:
        raise TypeError("Argument afeidxlist may not be None")
      copyback_afeidxlist = False
      if afeidxlist is None:
        afeidxlist_ = None
        memview_afeidxlist = None
      else:
        try:
          memview_afeidxlist = memoryview(afeidxlist)
        except TypeError:
          try:
            _tmparray_afeidxlist = array.array("q",afeidxlist)
          except TypeError:
            raise TypeError("Argument afeidxlist has wrong type") from None
          else:
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
        else:
          if memview_afeidxlist.ndim != 1:
            raise TypeError("Argument afeidxlist must be one-dimensional")
          if memview_afeidxlist.format != "q":
            _tmparray_afeidxlist = array.array("q",afeidxlist)
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",b)
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      _res_appendacc,_retargs_appendacc = self.__obj.appendacc_LOO_4(domidx,memview_afeidxlist,memview_b)
      if _res_appendacc != 0:
        _,_msg_appendacc = self.__getlasterror(_res_appendacc)
        raise Error(rescode(_res_appendacc),_msg_appendacc)
    def appendacc(self,*args,**kwds):
      """
      Appends an affine conic constraint to the task.
    
      appendacc(domidx,afeidxlist,b)
        [afeidxlist : array(int64)]  List of affine expression indexes.  
        [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
        [domidx : int64]  Domain index.  
      """
      return self.__appendacc_LOO_4(*args,**kwds)
    def __appendaccs_OOO_4(self,domidxs,afeidxlist,b):
      if domidxs is None:
        raise TypeError("Argument domidxs may not be None")
      copyback_domidxs = False
      if domidxs is None:
        domidxs_ = None
        memview_domidxs = None
      else:
        try:
          memview_domidxs = memoryview(domidxs)
        except TypeError:
          try:
            _tmparray_domidxs = array.array("q",domidxs)
          except TypeError:
            raise TypeError("Argument domidxs has wrong type") from None
          else:
            memview_domidxs = memoryview(_tmparray_domidxs)
            copyback_domidxs = True
            domidxs_ = _tmparray_domidxs
        else:
          if memview_domidxs.ndim != 1:
            raise TypeError("Argument domidxs must be one-dimensional")
          if memview_domidxs.format != "q":
            _tmparray_domidxs = array.array("q",domidxs)
            memview_domidxs = memoryview(_tmparray_domidxs)
            copyback_domidxs = True
            domidxs_ = _tmparray_domidxs
      if afeidxlist is None:
        raise TypeError("Argument afeidxlist may not be None")
      copyback_afeidxlist = False
      if afeidxlist is None:
        afeidxlist_ = None
        memview_afeidxlist = None
      else:
        try:
          memview_afeidxlist = memoryview(afeidxlist)
        except TypeError:
          try:
            _tmparray_afeidxlist = array.array("q",afeidxlist)
          except TypeError:
            raise TypeError("Argument afeidxlist has wrong type") from None
          else:
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
        else:
          if memview_afeidxlist.ndim != 1:
            raise TypeError("Argument afeidxlist must be one-dimensional")
          if memview_afeidxlist.format != "q":
            _tmparray_afeidxlist = array.array("q",afeidxlist)
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",b)
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      _res_appendaccs,_retargs_appendaccs = self.__obj.appendaccs_OOO_4(memview_domidxs,memview_afeidxlist,memview_b)
      if _res_appendaccs != 0:
        _,_msg_appendaccs = self.__getlasterror(_res_appendaccs)
        raise Error(rescode(_res_appendaccs),_msg_appendaccs)
    def appendaccs(self,*args,**kwds):
      """
      Appends a number of affine conic constraint to the task.
    
      appendaccs(domidxs,afeidxlist,b)
        [afeidxlist : array(int64)]  List of affine expression indexes.  
        [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
        [domidxs : array(int64)]  Domain indices.  
      """
      return self.__appendaccs_OOO_4(*args,**kwds)
    def __appendaccseq_LLO_4(self,domidx,afeidxfirst,b):
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",b)
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      _res_appendaccseq,_retargs_appendaccseq = self.__obj.appendaccseq_LLO_4(domidx,afeidxfirst,memview_b)
      if _res_appendaccseq != 0:
        _,_msg_appendaccseq = self.__getlasterror(_res_appendaccseq)
        raise Error(rescode(_res_appendaccseq),_msg_appendaccseq)
    def appendaccseq(self,*args,**kwds):
      """
      Appends an affine conic constraint to the task.
    
      appendaccseq(domidx,afeidxfirst,b)
        [afeidxfirst : int64]  Index of the first affine expression.  
        [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
        [domidx : int64]  Domain index.  
      """
      return self.__appendaccseq_LLO_4(*args,**kwds)
    def __appendaccsseq_OLLO_5(self,domidxs,numafeidx,afeidxfirst,b):
      if domidxs is None:
        raise TypeError("Argument domidxs may not be None")
      copyback_domidxs = False
      if domidxs is None:
        domidxs_ = None
        memview_domidxs = None
      else:
        try:
          memview_domidxs = memoryview(domidxs)
        except TypeError:
          try:
            _tmparray_domidxs = array.array("q",domidxs)
          except TypeError:
            raise TypeError("Argument domidxs has wrong type") from None
          else:
            memview_domidxs = memoryview(_tmparray_domidxs)
            copyback_domidxs = True
            domidxs_ = _tmparray_domidxs
        else:
          if memview_domidxs.ndim != 1:
            raise TypeError("Argument domidxs must be one-dimensional")
          if memview_domidxs.format != "q":
            _tmparray_domidxs = array.array("q",domidxs)
            memview_domidxs = memoryview(_tmparray_domidxs)
            copyback_domidxs = True
            domidxs_ = _tmparray_domidxs
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",b)
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      _res_appendaccsseq,_retargs_appendaccsseq = self.__obj.appendaccsseq_OLLO_5(memview_domidxs,numafeidx,afeidxfirst,memview_b)
      if _res_appendaccsseq != 0:
        _,_msg_appendaccsseq = self.__getlasterror(_res_appendaccsseq)
        raise Error(rescode(_res_appendaccsseq),_msg_appendaccsseq)
    def appendaccsseq(self,*args,**kwds):
      """
      Appends a number of affine conic constraint to the task.
    
      appendaccsseq(domidxs,numafeidx,afeidxfirst,b)
        [afeidxfirst : int64]  Index of the first affine expression.  
        [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
        [domidxs : array(int64)]  Domain indices.  
        [numafeidx : int64]  Number of affine expressions in the affine expression list (must equal the sum of dimensions of the domains).  
      """
      return self.__appendaccsseq_OLLO_5(*args,**kwds)
    def __putacc_LLOO_5(self,accidx,domidx,afeidxlist,b):
      if afeidxlist is None:
        raise TypeError("Argument afeidxlist may not be None")
      copyback_afeidxlist = False
      if afeidxlist is None:
        afeidxlist_ = None
        memview_afeidxlist = None
      else:
        try:
          memview_afeidxlist = memoryview(afeidxlist)
        except TypeError:
          try:
            _tmparray_afeidxlist = array.array("q",afeidxlist)
          except TypeError:
            raise TypeError("Argument afeidxlist has wrong type") from None
          else:
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
        else:
          if memview_afeidxlist.ndim != 1:
            raise TypeError("Argument afeidxlist must be one-dimensional")
          if memview_afeidxlist.format != "q":
            _tmparray_afeidxlist = array.array("q",afeidxlist)
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",b)
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      _res_putacc,_retargs_putacc = self.__obj.putacc_LLOO_5(accidx,domidx,memview_afeidxlist,memview_b)
      if _res_putacc != 0:
        _,_msg_putacc = self.__getlasterror(_res_putacc)
        raise Error(rescode(_res_putacc),_msg_putacc)
    def putacc(self,*args,**kwds):
      """
      Puts an affine conic constraint.
    
      putacc(accidx,domidx,afeidxlist,b)
        [accidx : int64]  Affine conic constraint index.  
        [afeidxlist : array(int64)]  List of affine expression indexes.  
        [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
        [domidx : int64]  Domain index.  
      """
      return self.__putacc_LLOO_5(*args,**kwds)
    def __putacclist_OOOO_5(self,accidxs,domidxs,afeidxlist,b):
      if accidxs is None:
        raise TypeError("Argument accidxs may not be None")
      copyback_accidxs = False
      if accidxs is None:
        accidxs_ = None
        memview_accidxs = None
      else:
        try:
          memview_accidxs = memoryview(accidxs)
        except TypeError:
          try:
            _tmparray_accidxs = array.array("q",accidxs)
          except TypeError:
            raise TypeError("Argument accidxs has wrong type") from None
          else:
            memview_accidxs = memoryview(_tmparray_accidxs)
            copyback_accidxs = True
            accidxs_ = _tmparray_accidxs
        else:
          if memview_accidxs.ndim != 1:
            raise TypeError("Argument accidxs must be one-dimensional")
          if memview_accidxs.format != "q":
            _tmparray_accidxs = array.array("q",accidxs)
            memview_accidxs = memoryview(_tmparray_accidxs)
            copyback_accidxs = True
            accidxs_ = _tmparray_accidxs
      if domidxs is None:
        raise TypeError("Argument domidxs may not be None")
      copyback_domidxs = False
      if domidxs is None:
        domidxs_ = None
        memview_domidxs = None
      else:
        try:
          memview_domidxs = memoryview(domidxs)
        except TypeError:
          try:
            _tmparray_domidxs = array.array("q",domidxs)
          except TypeError:
            raise TypeError("Argument domidxs has wrong type") from None
          else:
            memview_domidxs = memoryview(_tmparray_domidxs)
            copyback_domidxs = True
            domidxs_ = _tmparray_domidxs
        else:
          if memview_domidxs.ndim != 1:
            raise TypeError("Argument domidxs must be one-dimensional")
          if memview_domidxs.format != "q":
            _tmparray_domidxs = array.array("q",domidxs)
            memview_domidxs = memoryview(_tmparray_domidxs)
            copyback_domidxs = True
            domidxs_ = _tmparray_domidxs
      if afeidxlist is None:
        raise TypeError("Argument afeidxlist may not be None")
      copyback_afeidxlist = False
      if afeidxlist is None:
        afeidxlist_ = None
        memview_afeidxlist = None
      else:
        try:
          memview_afeidxlist = memoryview(afeidxlist)
        except TypeError:
          try:
            _tmparray_afeidxlist = array.array("q",afeidxlist)
          except TypeError:
            raise TypeError("Argument afeidxlist has wrong type") from None
          else:
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
        else:
          if memview_afeidxlist.ndim != 1:
            raise TypeError("Argument afeidxlist must be one-dimensional")
          if memview_afeidxlist.format != "q":
            _tmparray_afeidxlist = array.array("q",afeidxlist)
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",b)
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      _res_putacclist,_retargs_putacclist = self.__obj.putacclist_OOOO_5(memview_accidxs,memview_domidxs,memview_afeidxlist,memview_b)
      if _res_putacclist != 0:
        _,_msg_putacclist = self.__getlasterror(_res_putacclist)
        raise Error(rescode(_res_putacclist),_msg_putacclist)
    def putacclist(self,*args,**kwds):
      """
      Puts a number of affine conic constraints.
    
      putacclist(accidxs,domidxs,afeidxlist,b)
        [accidxs : array(int64)]  Affine conic constraint indices.  
        [afeidxlist : array(int64)]  List of affine expression indexes.  
        [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
        [domidxs : array(int64)]  Domain indices.  
      """
      return self.__putacclist_OOOO_5(*args,**kwds)
    def __putaccb_LO_3(self,accidx,b):
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",b)
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      _res_putaccb,_retargs_putaccb = self.__obj.putaccb_LO_3(accidx,memview_b)
      if _res_putaccb != 0:
        _,_msg_putaccb = self.__getlasterror(_res_putaccb)
        raise Error(rescode(_res_putaccb),_msg_putaccb)
    def putaccb(self,*args,**kwds):
      """
      Puts the constant vector b in an affine conic constraint.
    
      putaccb(accidx,b)
        [accidx : int64]  Affine conic constraint index.  
        [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, can be NULL.  
      """
      return self.__putaccb_LO_3(*args,**kwds)
    def __putaccbj_LLd_4(self,accidx,j,bj):
      _res_putaccbj,_retargs_putaccbj = self.__obj.putaccbj_LLd_4(accidx,j,bj)
      if _res_putaccbj != 0:
        _,_msg_putaccbj = self.__getlasterror(_res_putaccbj)
        raise Error(rescode(_res_putaccbj),_msg_putaccbj)
    def putaccbj(self,*args,**kwds):
      """
      Sets one element in the b vector of an affine conic constraint.
    
      putaccbj(accidx,j,bj)
        [accidx : int64]  Affine conic constraint index.  
        [bj : float64]  The new value of b[j].  
        [j : int64]  The index of an element in b to change.  
      """
      return self.__putaccbj_LLd_4(*args,**kwds)
    def __getaccdomain_L_2(self,accidx):
      _res_getaccdomain,_retargs_getaccdomain = self.__obj.getaccdomain_L_2(accidx)
      if _res_getaccdomain != 0:
        _,_msg_getaccdomain = self.__getlasterror(_res_getaccdomain)
        raise Error(rescode(_res_getaccdomain),_msg_getaccdomain)
      else:
        (domidx) = _retargs_getaccdomain
      return (domidx)
    def getaccdomain(self,*args,**kwds):
      """
      Obtains the domain appearing in the affine conic constraint.
    
      getaccdomain(accidx) -> (domidx)
        [accidx : int64]  The index of the affine conic constraint.  
        [domidx : int64]  The index of domain in the affine conic constraint.  
      """
      return self.__getaccdomain_L_2(*args,**kwds)
    def __getaccn_L_2(self,accidx):
      _res_getaccn,_retargs_getaccn = self.__obj.getaccn_L_2(accidx)
      if _res_getaccn != 0:
        _,_msg_getaccn = self.__getlasterror(_res_getaccn)
        raise Error(rescode(_res_getaccn),_msg_getaccn)
      else:
        (n) = _retargs_getaccn
      return (n)
    def getaccn(self,*args,**kwds):
      """
      Obtains the dimension of the affine conic constraint.
    
      getaccn(accidx) -> (n)
        [accidx : int64]  The index of the affine conic constraint.  
        [n : int64]  The dimension of the affine conic constraint (equal to the dimension of its domain).  
      """
      return self.__getaccn_L_2(*args,**kwds)
    def __getaccntot__1(self):
      _res_getaccntot,_retargs_getaccntot = self.__obj.getaccntot__1()
      if _res_getaccntot != 0:
        _,_msg_getaccntot = self.__getlasterror(_res_getaccntot)
        raise Error(rescode(_res_getaccntot),_msg_getaccntot)
      else:
        (n) = _retargs_getaccntot
      return (n)
    def getaccntot(self,*args,**kwds):
      """
      Obtains the total dimension of all affine conic constraints.
    
      getaccntot() -> (n)
        [n : int64]  The total dimension of all affine conic constraints.  
      """
      return self.__getaccntot__1(*args,**kwds)
    def __getaccafeidxlist_LO_3(self,accidx,afeidxlist):
      if afeidxlist is None:
        raise TypeError("Argument afeidxlist may not be None")
      copyback_afeidxlist = False
      if afeidxlist is None:
        afeidxlist_ = None
        memview_afeidxlist = None
      else:
        try:
          memview_afeidxlist = memoryview(afeidxlist)
        except TypeError:
          try:
            _tmparray_afeidxlist = array.array("q",[0 for _ in range(len(afeidxlist))])
          except TypeError:
            raise TypeError("Argument afeidxlist has wrong type") from None
          else:
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
        else:
          if memview_afeidxlist.ndim != 1:
            raise TypeError("Argument afeidxlist must be one-dimensional")
          if memview_afeidxlist.format != "q":
            _tmparray_afeidxlist = array.array("q",afeidxlist)
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
      _res_getaccafeidxlist,_retargs_getaccafeidxlist = self.__obj.getaccafeidxlist_LO_3(accidx,memview_afeidxlist)
      if _res_getaccafeidxlist != 0:
        _,_msg_getaccafeidxlist = self.__getlasterror(_res_getaccafeidxlist)
        raise Error(rescode(_res_getaccafeidxlist),_msg_getaccafeidxlist)
      if copyback_afeidxlist:
        for __tmp_1184 in range(len(afeidxlist)): afeidxlist[__tmp_1184] = afeidxlist_[__tmp_1184]
    def __getaccafeidxlist_LO_2(self,accidx):
      afeidxlist_ = bytearray(0)
      _res_getaccafeidxlist,_retargs_getaccafeidxlist = self.__obj.getaccafeidxlist_LO_2(accidx,afeidxlist_)
      if _res_getaccafeidxlist != 0:
        _,_msg_getaccafeidxlist = self.__getlasterror(_res_getaccafeidxlist)
        raise Error(rescode(_res_getaccafeidxlist),_msg_getaccafeidxlist)
      afeidxlist = array.array("q")
      afeidxlist.frombytes(afeidxlist_)
      return (afeidxlist)
    def getaccafeidxlist(self,*args,**kwds):
      """
      Obtains the list of affine expressions appearing in the affine conic constraint.
    
      getaccafeidxlist(accidx,afeidxlist)
      getaccafeidxlist(accidx) -> (afeidxlist)
        [accidx : int64]  Index of the affine conic constraint.  
        [afeidxlist : array(int64)]  List of indexes of affine expressions appearing in the constraint.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getaccafeidxlist_LO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getaccafeidxlist_LO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getaccb_LO_3(self,accidx,b):
      if b is None:
        raise TypeError("Argument b may not be None")
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",[0 for _ in range(len(b))])
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      _res_getaccb,_retargs_getaccb = self.__obj.getaccb_LO_3(accidx,memview_b)
      if _res_getaccb != 0:
        _,_msg_getaccb = self.__getlasterror(_res_getaccb)
        raise Error(rescode(_res_getaccb),_msg_getaccb)
      if copyback_b:
        for __tmp_1190 in range(len(b)): b[__tmp_1190] = b_[__tmp_1190]
    def __getaccb_LO_2(self,accidx):
      b_ = bytearray(0)
      _res_getaccb,_retargs_getaccb = self.__obj.getaccb_LO_2(accidx,b_)
      if _res_getaccb != 0:
        _,_msg_getaccb = self.__getlasterror(_res_getaccb)
        raise Error(rescode(_res_getaccb),_msg_getaccb)
      b = array.array("d")
      b.frombytes(b_)
      return (b)
    def getaccb(self,*args,**kwds):
      """
      Obtains the additional constant term vector appearing in the affine conic constraint.
    
      getaccb(accidx,b)
      getaccb(accidx) -> (b)
        [accidx : int64]  Index of the affine conic constraint.  
        [b : array(float64)]  The vector b appearing in the constraint.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getaccb_LO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getaccb_LO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getaccs_OOO_4(self,domidxlist,afeidxlist,b):
      if domidxlist is None:
        raise TypeError("Argument domidxlist may not be None")
      copyback_domidxlist = False
      if domidxlist is None:
        domidxlist_ = None
        memview_domidxlist = None
      else:
        try:
          memview_domidxlist = memoryview(domidxlist)
        except TypeError:
          try:
            _tmparray_domidxlist = array.array("q",[0 for _ in range(len(domidxlist))])
          except TypeError:
            raise TypeError("Argument domidxlist has wrong type") from None
          else:
            memview_domidxlist = memoryview(_tmparray_domidxlist)
            copyback_domidxlist = True
            domidxlist_ = _tmparray_domidxlist
        else:
          if memview_domidxlist.ndim != 1:
            raise TypeError("Argument domidxlist must be one-dimensional")
          if memview_domidxlist.format != "q":
            _tmparray_domidxlist = array.array("q",domidxlist)
            memview_domidxlist = memoryview(_tmparray_domidxlist)
            copyback_domidxlist = True
            domidxlist_ = _tmparray_domidxlist
      if afeidxlist is None:
        raise TypeError("Argument afeidxlist may not be None")
      copyback_afeidxlist = False
      if afeidxlist is None:
        afeidxlist_ = None
        memview_afeidxlist = None
      else:
        try:
          memview_afeidxlist = memoryview(afeidxlist)
        except TypeError:
          try:
            _tmparray_afeidxlist = array.array("q",[0 for _ in range(len(afeidxlist))])
          except TypeError:
            raise TypeError("Argument afeidxlist has wrong type") from None
          else:
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
        else:
          if memview_afeidxlist.ndim != 1:
            raise TypeError("Argument afeidxlist must be one-dimensional")
          if memview_afeidxlist.format != "q":
            _tmparray_afeidxlist = array.array("q",afeidxlist)
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
      if b is None:
        raise TypeError("Argument b may not be None")
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",[0 for _ in range(len(b))])
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      _res_getaccs,_retargs_getaccs = self.__obj.getaccs_OOO_4(memview_domidxlist,memview_afeidxlist,memview_b)
      if _res_getaccs != 0:
        _,_msg_getaccs = self.__getlasterror(_res_getaccs)
        raise Error(rescode(_res_getaccs),_msg_getaccs)
      if copyback_domidxlist:
        for __tmp_1196 in range(len(domidxlist)): domidxlist[__tmp_1196] = domidxlist_[__tmp_1196]
      if copyback_afeidxlist:
        for __tmp_1199 in range(len(afeidxlist)): afeidxlist[__tmp_1199] = afeidxlist_[__tmp_1199]
      if copyback_b:
        for __tmp_1202 in range(len(b)): b[__tmp_1202] = b_[__tmp_1202]
    def __getaccs_OOO_1(self):
      domidxlist_ = bytearray(0)
      afeidxlist_ = bytearray(0)
      b_ = bytearray(0)
      _res_getaccs,_retargs_getaccs = self.__obj.getaccs_OOO_1(domidxlist_,afeidxlist_,b_)
      if _res_getaccs != 0:
        _,_msg_getaccs = self.__getlasterror(_res_getaccs)
        raise Error(rescode(_res_getaccs),_msg_getaccs)
      domidxlist = array.array("q")
      domidxlist.frombytes(domidxlist_)
      afeidxlist = array.array("q")
      afeidxlist.frombytes(afeidxlist_)
      b = array.array("d")
      b.frombytes(b_)
      return (domidxlist,afeidxlist,b)
    def getaccs(self,*args,**kwds):
      """
      Obtains full data of all affine conic constraints.
    
      getaccs(domidxlist,afeidxlist,b)
      getaccs() -> (domidxlist,afeidxlist,b)
        [afeidxlist : array(int64)]  The concatenation of index lists of affine expressions appearing in all affine conic constraints.  
        [b : array(float64)]  The concatenation of vectors b appearing in all affine conic constraints.  
        [domidxlist : array(int64)]  The list of domains appearing in all affine conic constraints.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getaccs_OOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getaccs_OOO_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getaccfnumnz__1(self):
      _res_getaccfnumnz,_retargs_getaccfnumnz = self.__obj.getaccfnumnz__1()
      if _res_getaccfnumnz != 0:
        _,_msg_getaccfnumnz = self.__getlasterror(_res_getaccfnumnz)
        raise Error(rescode(_res_getaccfnumnz),_msg_getaccfnumnz)
      else:
        (accfnnz) = _retargs_getaccfnumnz
      return (accfnnz)
    def getaccfnumnz(self,*args,**kwds):
      """
      Obtains the total number of nonzeros in the ACC implied F matrix.
    
      getaccfnumnz() -> (accfnnz)
        [accfnnz : int64]  Number of nonzeros in the F matrix implied by ACCs.  
      """
      return self.__getaccfnumnz__1(*args,**kwds)
    def __getaccftrip_OOO_4(self,frow,fcol,fval):
      if frow is None:
        raise TypeError("Argument frow may not be None")
      copyback_frow = False
      if frow is None:
        frow_ = None
        memview_frow = None
      else:
        try:
          memview_frow = memoryview(frow)
        except TypeError:
          try:
            _tmparray_frow = array.array("q",[0 for _ in range(len(frow))])
          except TypeError:
            raise TypeError("Argument frow has wrong type") from None
          else:
            memview_frow = memoryview(_tmparray_frow)
            copyback_frow = True
            frow_ = _tmparray_frow
        else:
          if memview_frow.ndim != 1:
            raise TypeError("Argument frow must be one-dimensional")
          if memview_frow.format != "q":
            _tmparray_frow = array.array("q",frow)
            memview_frow = memoryview(_tmparray_frow)
            copyback_frow = True
            frow_ = _tmparray_frow
      if fcol is None:
        raise TypeError("Argument fcol may not be None")
      copyback_fcol = False
      if fcol is None:
        fcol_ = None
        memview_fcol = None
      else:
        try:
          memview_fcol = memoryview(fcol)
        except TypeError:
          try:
            _tmparray_fcol = array.array("i",[0 for _ in range(len(fcol))])
          except TypeError:
            raise TypeError("Argument fcol has wrong type") from None
          else:
            memview_fcol = memoryview(_tmparray_fcol)
            copyback_fcol = True
            fcol_ = _tmparray_fcol
        else:
          if memview_fcol.ndim != 1:
            raise TypeError("Argument fcol must be one-dimensional")
          if memview_fcol.format != "i":
            _tmparray_fcol = array.array("i",fcol)
            memview_fcol = memoryview(_tmparray_fcol)
            copyback_fcol = True
            fcol_ = _tmparray_fcol
      if fval is None:
        raise TypeError("Argument fval may not be None")
      copyback_fval = False
      if fval is None:
        fval_ = None
        memview_fval = None
      else:
        try:
          memview_fval = memoryview(fval)
        except TypeError:
          try:
            _tmparray_fval = array.array("d",[0 for _ in range(len(fval))])
          except TypeError:
            raise TypeError("Argument fval has wrong type") from None
          else:
            memview_fval = memoryview(_tmparray_fval)
            copyback_fval = True
            fval_ = _tmparray_fval
        else:
          if memview_fval.ndim != 1:
            raise TypeError("Argument fval must be one-dimensional")
          if memview_fval.format != "d":
            _tmparray_fval = array.array("d",fval)
            memview_fval = memoryview(_tmparray_fval)
            copyback_fval = True
            fval_ = _tmparray_fval
      _res_getaccftrip,_retargs_getaccftrip = self.__obj.getaccftrip_OOO_4(memview_frow,memview_fcol,memview_fval)
      if _res_getaccftrip != 0:
        _,_msg_getaccftrip = self.__getlasterror(_res_getaccftrip)
        raise Error(rescode(_res_getaccftrip),_msg_getaccftrip)
      if copyback_frow:
        for __tmp_1214 in range(len(frow)): frow[__tmp_1214] = frow_[__tmp_1214]
      if copyback_fcol:
        for __tmp_1217 in range(len(fcol)): fcol[__tmp_1217] = fcol_[__tmp_1217]
      if copyback_fval:
        for __tmp_1220 in range(len(fval)): fval[__tmp_1220] = fval_[__tmp_1220]
    def __getaccftrip_OOO_1(self):
      frow_ = bytearray(0)
      fcol_ = bytearray(0)
      fval_ = bytearray(0)
      _res_getaccftrip,_retargs_getaccftrip = self.__obj.getaccftrip_OOO_1(frow_,fcol_,fval_)
      if _res_getaccftrip != 0:
        _,_msg_getaccftrip = self.__getlasterror(_res_getaccftrip)
        raise Error(rescode(_res_getaccftrip),_msg_getaccftrip)
      frow = array.array("q")
      frow.frombytes(frow_)
      fcol = array.array("i")
      fcol.frombytes(fcol_)
      fval = array.array("d")
      fval.frombytes(fval_)
      return (frow,fcol,fval)
    def getaccftrip(self,*args,**kwds):
      """
      Obtains the F matrix (implied by the AFE ordering within the ACCs) in triplet format.
    
      getaccftrip(frow,fcol,fval)
      getaccftrip() -> (frow,fcol,fval)
        [fcol : array(int32)]  Column indices of nonzeros in the implied F matrix.  
        [frow : array(int64)]  Row indices of nonzeros in the implied F matrix.  
        [fval : array(float64)]  Values of nonzero entries in the implied F matrix.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 4: return self.__getaccftrip_OOO_4(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getaccftrip_OOO_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getaccgvector_O_2(self,g):
      copyback_g = False
      if g is None:
        g_ = None
        memview_g = None
      else:
        try:
          memview_g = memoryview(g)
        except TypeError:
          try:
            _tmparray_g = array.array("d",[0 for _ in range(len(g))])
          except TypeError:
            raise TypeError("Argument g has wrong type") from None
          else:
            memview_g = memoryview(_tmparray_g)
            copyback_g = True
            g_ = _tmparray_g
        else:
          if memview_g.ndim != 1:
            raise TypeError("Argument g must be one-dimensional")
          if memview_g.format != "d":
            _tmparray_g = array.array("d",g)
            memview_g = memoryview(_tmparray_g)
            copyback_g = True
            g_ = _tmparray_g
      _res_getaccgvector,_retargs_getaccgvector = self.__obj.getaccgvector_O_2(memview_g)
      if _res_getaccgvector != 0:
        _,_msg_getaccgvector = self.__getlasterror(_res_getaccgvector)
        raise Error(rescode(_res_getaccgvector),_msg_getaccgvector)
      if copyback_g:
        for __tmp_1232 in range(len(g)): g[__tmp_1232] = g_[__tmp_1232]
    def __getaccgvector_O_1(self):
      g_ = bytearray(0)
      _res_getaccgvector,_retargs_getaccgvector = self.__obj.getaccgvector_O_1(g_)
      if _res_getaccgvector != 0:
        _,_msg_getaccgvector = self.__getlasterror(_res_getaccgvector)
        raise Error(rescode(_res_getaccgvector),_msg_getaccgvector)
      g = array.array("d")
      g.frombytes(g_)
      return (g)
    def getaccgvector(self,*args,**kwds):
      """
      The g vector as used within the ACCs.
    
      getaccgvector(g)
      getaccgvector() -> (g)
        [g : array(float64)]  The g vector as used within the ACCs.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 2: return self.__getaccgvector_O_2(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getaccgvector_O_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getaccbarfnumblocktriplets__1(self):
      _res_getaccbarfnumblocktriplets,_retargs_getaccbarfnumblocktriplets = self.__obj.getaccbarfnumblocktriplets__1()
      if _res_getaccbarfnumblocktriplets != 0:
        _,_msg_getaccbarfnumblocktriplets = self.__getlasterror(_res_getaccbarfnumblocktriplets)
        raise Error(rescode(_res_getaccbarfnumblocktriplets),_msg_getaccbarfnumblocktriplets)
      else:
        (numtrip) = _retargs_getaccbarfnumblocktriplets
      return (numtrip)
    def getaccbarfnumblocktriplets(self,*args,**kwds):
      """
      Obtains an upper bound on the number of elements in the block triplet form of barf, as used within the ACCs.
    
      getaccbarfnumblocktriplets() -> (numtrip)
        [numtrip : int64]  An upper bound on the number of elements in the block triplet form of barf, as used within the ACCs.  
      """
      return self.__getaccbarfnumblocktriplets__1(*args,**kwds)
    def __getaccbarfblocktriplet_OOOOO_6(self,acc_afe,bar_var,blk_row,blk_col,blk_val):
      if acc_afe is None:
        raise TypeError("Argument acc_afe may not be None")
      copyback_acc_afe = False
      if acc_afe is None:
        acc_afe_ = None
        memview_acc_afe = None
      else:
        try:
          memview_acc_afe = memoryview(acc_afe)
        except TypeError:
          try:
            _tmparray_acc_afe = array.array("q",[0 for _ in range(len(acc_afe))])
          except TypeError:
            raise TypeError("Argument acc_afe has wrong type") from None
          else:
            memview_acc_afe = memoryview(_tmparray_acc_afe)
            copyback_acc_afe = True
            acc_afe_ = _tmparray_acc_afe
        else:
          if memview_acc_afe.ndim != 1:
            raise TypeError("Argument acc_afe must be one-dimensional")
          if memview_acc_afe.format != "q":
            _tmparray_acc_afe = array.array("q",acc_afe)
            memview_acc_afe = memoryview(_tmparray_acc_afe)
            copyback_acc_afe = True
            acc_afe_ = _tmparray_acc_afe
      if bar_var is None:
        raise TypeError("Argument bar_var may not be None")
      copyback_bar_var = False
      if bar_var is None:
        bar_var_ = None
        memview_bar_var = None
      else:
        try:
          memview_bar_var = memoryview(bar_var)
        except TypeError:
          try:
            _tmparray_bar_var = array.array("i",[0 for _ in range(len(bar_var))])
          except TypeError:
            raise TypeError("Argument bar_var has wrong type") from None
          else:
            memview_bar_var = memoryview(_tmparray_bar_var)
            copyback_bar_var = True
            bar_var_ = _tmparray_bar_var
        else:
          if memview_bar_var.ndim != 1:
            raise TypeError("Argument bar_var must be one-dimensional")
          if memview_bar_var.format != "i":
            _tmparray_bar_var = array.array("i",bar_var)
            memview_bar_var = memoryview(_tmparray_bar_var)
            copyback_bar_var = True
            bar_var_ = _tmparray_bar_var
      if blk_row is None:
        raise TypeError("Argument blk_row may not be None")
      copyback_blk_row = False
      if blk_row is None:
        blk_row_ = None
        memview_blk_row = None
      else:
        try:
          memview_blk_row = memoryview(blk_row)
        except TypeError:
          try:
            _tmparray_blk_row = array.array("i",[0 for _ in range(len(blk_row))])
          except TypeError:
            raise TypeError("Argument blk_row has wrong type") from None
          else:
            memview_blk_row = memoryview(_tmparray_blk_row)
            copyback_blk_row = True
            blk_row_ = _tmparray_blk_row
        else:
          if memview_blk_row.ndim != 1:
            raise TypeError("Argument blk_row must be one-dimensional")
          if memview_blk_row.format != "i":
            _tmparray_blk_row = array.array("i",blk_row)
            memview_blk_row = memoryview(_tmparray_blk_row)
            copyback_blk_row = True
            blk_row_ = _tmparray_blk_row
      if blk_col is None:
        raise TypeError("Argument blk_col may not be None")
      copyback_blk_col = False
      if blk_col is None:
        blk_col_ = None
        memview_blk_col = None
      else:
        try:
          memview_blk_col = memoryview(blk_col)
        except TypeError:
          try:
            _tmparray_blk_col = array.array("i",[0 for _ in range(len(blk_col))])
          except TypeError:
            raise TypeError("Argument blk_col has wrong type") from None
          else:
            memview_blk_col = memoryview(_tmparray_blk_col)
            copyback_blk_col = True
            blk_col_ = _tmparray_blk_col
        else:
          if memview_blk_col.ndim != 1:
            raise TypeError("Argument blk_col must be one-dimensional")
          if memview_blk_col.format != "i":
            _tmparray_blk_col = array.array("i",blk_col)
            memview_blk_col = memoryview(_tmparray_blk_col)
            copyback_blk_col = True
            blk_col_ = _tmparray_blk_col
      if blk_val is None:
        raise TypeError("Argument blk_val may not be None")
      copyback_blk_val = False
      if blk_val is None:
        blk_val_ = None
        memview_blk_val = None
      else:
        try:
          memview_blk_val = memoryview(blk_val)
        except TypeError:
          try:
            _tmparray_blk_val = array.array("d",[0 for _ in range(len(blk_val))])
          except TypeError:
            raise TypeError("Argument blk_val has wrong type") from None
          else:
            memview_blk_val = memoryview(_tmparray_blk_val)
            copyback_blk_val = True
            blk_val_ = _tmparray_blk_val
        else:
          if memview_blk_val.ndim != 1:
            raise TypeError("Argument blk_val must be one-dimensional")
          if memview_blk_val.format != "d":
            _tmparray_blk_val = array.array("d",blk_val)
            memview_blk_val = memoryview(_tmparray_blk_val)
            copyback_blk_val = True
            blk_val_ = _tmparray_blk_val
      _res_getaccbarfblocktriplet,_retargs_getaccbarfblocktriplet = self.__obj.getaccbarfblocktriplet_OOOOO_6(memview_acc_afe,memview_bar_var,memview_blk_row,memview_blk_col,memview_blk_val)
      if _res_getaccbarfblocktriplet != 0:
        _,_msg_getaccbarfblocktriplet = self.__getlasterror(_res_getaccbarfblocktriplet)
        raise Error(rescode(_res_getaccbarfblocktriplet),_msg_getaccbarfblocktriplet)
      else:
        (numtrip) = _retargs_getaccbarfblocktriplet
      if copyback_acc_afe:
        for __tmp_1238 in range(len(acc_afe)): acc_afe[__tmp_1238] = acc_afe_[__tmp_1238]
      if copyback_bar_var:
        for __tmp_1239 in range(len(bar_var)): bar_var[__tmp_1239] = bar_var_[__tmp_1239]
      if copyback_blk_row:
        for __tmp_1240 in range(len(blk_row)): blk_row[__tmp_1240] = blk_row_[__tmp_1240]
      if copyback_blk_col:
        for __tmp_1241 in range(len(blk_col)): blk_col[__tmp_1241] = blk_col_[__tmp_1241]
      if copyback_blk_val:
        for __tmp_1242 in range(len(blk_val)): blk_val[__tmp_1242] = blk_val_[__tmp_1242]
      return (numtrip)
    def __getaccbarfblocktriplet_OOOOO_1(self):
      acc_afe_ = bytearray(0)
      bar_var_ = bytearray(0)
      blk_row_ = bytearray(0)
      blk_col_ = bytearray(0)
      blk_val_ = bytearray(0)
      _res_getaccbarfblocktriplet,_retargs_getaccbarfblocktriplet = self.__obj.getaccbarfblocktriplet_OOOOO_1(acc_afe_,bar_var_,blk_row_,blk_col_,blk_val_)
      if _res_getaccbarfblocktriplet != 0:
        _,_msg_getaccbarfblocktriplet = self.__getlasterror(_res_getaccbarfblocktriplet)
        raise Error(rescode(_res_getaccbarfblocktriplet),_msg_getaccbarfblocktriplet)
      else:
        (numtrip) = _retargs_getaccbarfblocktriplet
      acc_afe = array.array("q")
      acc_afe.frombytes(acc_afe_)
      bar_var = array.array("i")
      bar_var.frombytes(bar_var_)
      blk_row = array.array("i")
      blk_row.frombytes(blk_row_)
      blk_col = array.array("i")
      blk_col.frombytes(blk_col_)
      blk_val = array.array("d")
      blk_val.frombytes(blk_val_)
      return (numtrip,acc_afe,bar_var,blk_row,blk_col,blk_val)
    def getaccbarfblocktriplet(self,*args,**kwds):
      """
      Obtains barF, implied by the ACCs, in block triplet form.
    
      getaccbarfblocktriplet(acc_afe,bar_var,blk_row,blk_col,blk_val) -> (numtrip)
      getaccbarfblocktriplet() -> 
                            (numtrip,
                             acc_afe,
                             bar_var,
                             blk_row,
                             blk_col,
                             blk_val)
        [acc_afe : array(int64)]  Index of the AFE within the concatenated list of AFEs in ACCs.  
        [bar_var : array(int32)]  Symmetric matrix variable index.  
        [blk_col : array(int32)]  Block column index.  
        [blk_row : array(int32)]  Block row index.  
        [blk_val : array(float64)]  The numerical value associated with each block triplet.  
        [numtrip : int64]  Number of elements in the block triplet form.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__getaccbarfblocktriplet_OOOOO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getaccbarfblocktriplet_OOOOO_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __appenddjcs_L_2(self,num):
      _res_appenddjcs,_retargs_appenddjcs = self.__obj.appenddjcs_L_2(num)
      if _res_appenddjcs != 0:
        _,_msg_appenddjcs = self.__getlasterror(_res_appenddjcs)
        raise Error(rescode(_res_appenddjcs),_msg_appenddjcs)
    def appenddjcs(self,*args,**kwds):
      """
      Appends a number of empty disjunctive constraints to the task.
    
      appenddjcs(num)
        [num : int64]  Number of empty disjunctive constraints which should be appended.  
      """
      return self.__appenddjcs_L_2(*args,**kwds)
    def __putdjc_LOOOO_6(self,djcidx,domidxlist,afeidxlist,b,termsizelist):
      if domidxlist is None:
        raise TypeError("Argument domidxlist may not be None")
      copyback_domidxlist = False
      if domidxlist is None:
        domidxlist_ = None
        memview_domidxlist = None
      else:
        try:
          memview_domidxlist = memoryview(domidxlist)
        except TypeError:
          try:
            _tmparray_domidxlist = array.array("q",domidxlist)
          except TypeError:
            raise TypeError("Argument domidxlist has wrong type") from None
          else:
            memview_domidxlist = memoryview(_tmparray_domidxlist)
            copyback_domidxlist = True
            domidxlist_ = _tmparray_domidxlist
        else:
          if memview_domidxlist.ndim != 1:
            raise TypeError("Argument domidxlist must be one-dimensional")
          if memview_domidxlist.format != "q":
            _tmparray_domidxlist = array.array("q",domidxlist)
            memview_domidxlist = memoryview(_tmparray_domidxlist)
            copyback_domidxlist = True
            domidxlist_ = _tmparray_domidxlist
      if afeidxlist is None:
        raise TypeError("Argument afeidxlist may not be None")
      copyback_afeidxlist = False
      if afeidxlist is None:
        afeidxlist_ = None
        memview_afeidxlist = None
      else:
        try:
          memview_afeidxlist = memoryview(afeidxlist)
        except TypeError:
          try:
            _tmparray_afeidxlist = array.array("q",afeidxlist)
          except TypeError:
            raise TypeError("Argument afeidxlist has wrong type") from None
          else:
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
        else:
          if memview_afeidxlist.ndim != 1:
            raise TypeError("Argument afeidxlist must be one-dimensional")
          if memview_afeidxlist.format != "q":
            _tmparray_afeidxlist = array.array("q",afeidxlist)
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",b)
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      if termsizelist is None:
        raise TypeError("Argument termsizelist may not be None")
      copyback_termsizelist = False
      if termsizelist is None:
        termsizelist_ = None
        memview_termsizelist = None
      else:
        try:
          memview_termsizelist = memoryview(termsizelist)
        except TypeError:
          try:
            _tmparray_termsizelist = array.array("q",termsizelist)
          except TypeError:
            raise TypeError("Argument termsizelist has wrong type") from None
          else:
            memview_termsizelist = memoryview(_tmparray_termsizelist)
            copyback_termsizelist = True
            termsizelist_ = _tmparray_termsizelist
        else:
          if memview_termsizelist.ndim != 1:
            raise TypeError("Argument termsizelist must be one-dimensional")
          if memview_termsizelist.format != "q":
            _tmparray_termsizelist = array.array("q",termsizelist)
            memview_termsizelist = memoryview(_tmparray_termsizelist)
            copyback_termsizelist = True
            termsizelist_ = _tmparray_termsizelist
      _res_putdjc,_retargs_putdjc = self.__obj.putdjc_LOOOO_6(djcidx,memview_domidxlist,memview_afeidxlist,memview_b,memview_termsizelist)
      if _res_putdjc != 0:
        _,_msg_putdjc = self.__getlasterror(_res_putdjc)
        raise Error(rescode(_res_putdjc),_msg_putdjc)
    def putdjc(self,*args,**kwds):
      """
      Inputs a disjunctive constraint.
    
      putdjc(djcidx,
             domidxlist,
             afeidxlist,
             b,
             termsizelist)
        [afeidxlist : array(int64)]  List of affine expression indexes.  
        [b : array(float64)]  The vector of constant terms added to affine expressions.  
        [djcidx : int64]  Index of the disjunctive constraint.  
        [domidxlist : array(int64)]  List of domain indexes.  
        [termsizelist : array(int64)]  List of term sizes.  
      """
      return self.__putdjc_LOOOO_6(*args,**kwds)
    def __putdjcslice_LLOOOOO_8(self,idxfirst,idxlast,domidxlist,afeidxlist,b,termsizelist,termsindjc):
      if domidxlist is None:
        raise TypeError("Argument domidxlist may not be None")
      copyback_domidxlist = False
      if domidxlist is None:
        domidxlist_ = None
        memview_domidxlist = None
      else:
        try:
          memview_domidxlist = memoryview(domidxlist)
        except TypeError:
          try:
            _tmparray_domidxlist = array.array("q",domidxlist)
          except TypeError:
            raise TypeError("Argument domidxlist has wrong type") from None
          else:
            memview_domidxlist = memoryview(_tmparray_domidxlist)
            copyback_domidxlist = True
            domidxlist_ = _tmparray_domidxlist
        else:
          if memview_domidxlist.ndim != 1:
            raise TypeError("Argument domidxlist must be one-dimensional")
          if memview_domidxlist.format != "q":
            _tmparray_domidxlist = array.array("q",domidxlist)
            memview_domidxlist = memoryview(_tmparray_domidxlist)
            copyback_domidxlist = True
            domidxlist_ = _tmparray_domidxlist
      if afeidxlist is None:
        raise TypeError("Argument afeidxlist may not be None")
      copyback_afeidxlist = False
      if afeidxlist is None:
        afeidxlist_ = None
        memview_afeidxlist = None
      else:
        try:
          memview_afeidxlist = memoryview(afeidxlist)
        except TypeError:
          try:
            _tmparray_afeidxlist = array.array("q",afeidxlist)
          except TypeError:
            raise TypeError("Argument afeidxlist has wrong type") from None
          else:
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
        else:
          if memview_afeidxlist.ndim != 1:
            raise TypeError("Argument afeidxlist must be one-dimensional")
          if memview_afeidxlist.format != "q":
            _tmparray_afeidxlist = array.array("q",afeidxlist)
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",b)
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      if termsizelist is None:
        raise TypeError("Argument termsizelist may not be None")
      copyback_termsizelist = False
      if termsizelist is None:
        termsizelist_ = None
        memview_termsizelist = None
      else:
        try:
          memview_termsizelist = memoryview(termsizelist)
        except TypeError:
          try:
            _tmparray_termsizelist = array.array("q",termsizelist)
          except TypeError:
            raise TypeError("Argument termsizelist has wrong type") from None
          else:
            memview_termsizelist = memoryview(_tmparray_termsizelist)
            copyback_termsizelist = True
            termsizelist_ = _tmparray_termsizelist
        else:
          if memview_termsizelist.ndim != 1:
            raise TypeError("Argument termsizelist must be one-dimensional")
          if memview_termsizelist.format != "q":
            _tmparray_termsizelist = array.array("q",termsizelist)
            memview_termsizelist = memoryview(_tmparray_termsizelist)
            copyback_termsizelist = True
            termsizelist_ = _tmparray_termsizelist
      if termsindjc is None:
        raise TypeError("Argument termsindjc may not be None")
      copyback_termsindjc = False
      if termsindjc is None:
        termsindjc_ = None
        memview_termsindjc = None
      else:
        try:
          memview_termsindjc = memoryview(termsindjc)
        except TypeError:
          try:
            _tmparray_termsindjc = array.array("q",termsindjc)
          except TypeError:
            raise TypeError("Argument termsindjc has wrong type") from None
          else:
            memview_termsindjc = memoryview(_tmparray_termsindjc)
            copyback_termsindjc = True
            termsindjc_ = _tmparray_termsindjc
        else:
          if memview_termsindjc.ndim != 1:
            raise TypeError("Argument termsindjc must be one-dimensional")
          if memview_termsindjc.format != "q":
            _tmparray_termsindjc = array.array("q",termsindjc)
            memview_termsindjc = memoryview(_tmparray_termsindjc)
            copyback_termsindjc = True
            termsindjc_ = _tmparray_termsindjc
      _res_putdjcslice,_retargs_putdjcslice = self.__obj.putdjcslice_LLOOOOO_8(idxfirst,idxlast,memview_domidxlist,memview_afeidxlist,memview_b,memview_termsizelist,memview_termsindjc)
      if _res_putdjcslice != 0:
        _,_msg_putdjcslice = self.__getlasterror(_res_putdjcslice)
        raise Error(rescode(_res_putdjcslice),_msg_putdjcslice)
    def putdjcslice(self,*args,**kwds):
      """
      Inputs a slice of disjunctive constraints.
    
      putdjcslice(idxfirst,
                  idxlast,
                  domidxlist,
                  afeidxlist,
                  b,
                  termsizelist,
                  termsindjc)
        [afeidxlist : array(int64)]  List of affine expression indexes.  
        [b : array(float64)]  The vector of constant terms added to affine expressions. Optional, may be NULL.  
        [domidxlist : array(int64)]  List of domain indexes.  
        [idxfirst : int64]  Index of the first disjunctive constraint in the slice.  
        [idxlast : int64]  Index of the last disjunctive constraint in the slice plus 1.  
        [termsindjc : array(int64)]  Number of terms in each of the disjunctive constraints in the slice.  
        [termsizelist : array(int64)]  List of term sizes.  
      """
      return self.__putdjcslice_LLOOOOO_8(*args,**kwds)
    def __getdjcdomainidxlist_LO_3(self,djcidx,domidxlist):
      if domidxlist is None:
        raise TypeError("Argument domidxlist may not be None")
      copyback_domidxlist = False
      if domidxlist is None:
        domidxlist_ = None
        memview_domidxlist = None
      else:
        try:
          memview_domidxlist = memoryview(domidxlist)
        except TypeError:
          try:
            _tmparray_domidxlist = array.array("q",[0 for _ in range(len(domidxlist))])
          except TypeError:
            raise TypeError("Argument domidxlist has wrong type") from None
          else:
            memview_domidxlist = memoryview(_tmparray_domidxlist)
            copyback_domidxlist = True
            domidxlist_ = _tmparray_domidxlist
        else:
          if memview_domidxlist.ndim != 1:
            raise TypeError("Argument domidxlist must be one-dimensional")
          if memview_domidxlist.format != "q":
            _tmparray_domidxlist = array.array("q",domidxlist)
            memview_domidxlist = memoryview(_tmparray_domidxlist)
            copyback_domidxlist = True
            domidxlist_ = _tmparray_domidxlist
      _res_getdjcdomainidxlist,_retargs_getdjcdomainidxlist = self.__obj.getdjcdomainidxlist_LO_3(djcidx,memview_domidxlist)
      if _res_getdjcdomainidxlist != 0:
        _,_msg_getdjcdomainidxlist = self.__getlasterror(_res_getdjcdomainidxlist)
        raise Error(rescode(_res_getdjcdomainidxlist),_msg_getdjcdomainidxlist)
      if copyback_domidxlist:
        for __tmp_1270 in range(len(domidxlist)): domidxlist[__tmp_1270] = domidxlist_[__tmp_1270]
    def __getdjcdomainidxlist_LO_2(self,djcidx):
      domidxlist_ = bytearray(0)
      _res_getdjcdomainidxlist,_retargs_getdjcdomainidxlist = self.__obj.getdjcdomainidxlist_LO_2(djcidx,domidxlist_)
      if _res_getdjcdomainidxlist != 0:
        _,_msg_getdjcdomainidxlist = self.__getlasterror(_res_getdjcdomainidxlist)
        raise Error(rescode(_res_getdjcdomainidxlist),_msg_getdjcdomainidxlist)
      domidxlist = array.array("q")
      domidxlist.frombytes(domidxlist_)
      return (domidxlist)
    def getdjcdomainidxlist(self,*args,**kwds):
      """
      Obtains the list of domain indexes in a disjunctive constraint.
    
      getdjcdomainidxlist(djcidx,domidxlist)
      getdjcdomainidxlist(djcidx) -> (domidxlist)
        [djcidx : int64]  Index of the disjunctive constraint.  
        [domidxlist : array(int64)]  List of term sizes.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getdjcdomainidxlist_LO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getdjcdomainidxlist_LO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getdjcafeidxlist_LO_3(self,djcidx,afeidxlist):
      if afeidxlist is None:
        raise TypeError("Argument afeidxlist may not be None")
      copyback_afeidxlist = False
      if afeidxlist is None:
        afeidxlist_ = None
        memview_afeidxlist = None
      else:
        try:
          memview_afeidxlist = memoryview(afeidxlist)
        except TypeError:
          try:
            _tmparray_afeidxlist = array.array("q",[0 for _ in range(len(afeidxlist))])
          except TypeError:
            raise TypeError("Argument afeidxlist has wrong type") from None
          else:
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
        else:
          if memview_afeidxlist.ndim != 1:
            raise TypeError("Argument afeidxlist must be one-dimensional")
          if memview_afeidxlist.format != "q":
            _tmparray_afeidxlist = array.array("q",afeidxlist)
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
      _res_getdjcafeidxlist,_retargs_getdjcafeidxlist = self.__obj.getdjcafeidxlist_LO_3(djcidx,memview_afeidxlist)
      if _res_getdjcafeidxlist != 0:
        _,_msg_getdjcafeidxlist = self.__getlasterror(_res_getdjcafeidxlist)
        raise Error(rescode(_res_getdjcafeidxlist),_msg_getdjcafeidxlist)
      if copyback_afeidxlist:
        for __tmp_1276 in range(len(afeidxlist)): afeidxlist[__tmp_1276] = afeidxlist_[__tmp_1276]
    def __getdjcafeidxlist_LO_2(self,djcidx):
      afeidxlist_ = bytearray(0)
      _res_getdjcafeidxlist,_retargs_getdjcafeidxlist = self.__obj.getdjcafeidxlist_LO_2(djcidx,afeidxlist_)
      if _res_getdjcafeidxlist != 0:
        _,_msg_getdjcafeidxlist = self.__getlasterror(_res_getdjcafeidxlist)
        raise Error(rescode(_res_getdjcafeidxlist),_msg_getdjcafeidxlist)
      afeidxlist = array.array("q")
      afeidxlist.frombytes(afeidxlist_)
      return (afeidxlist)
    def getdjcafeidxlist(self,*args,**kwds):
      """
      Obtains the list of affine expression indexes in a disjunctive constraint.
    
      getdjcafeidxlist(djcidx,afeidxlist)
      getdjcafeidxlist(djcidx) -> (afeidxlist)
        [afeidxlist : array(int64)]  List of affine expression indexes.  
        [djcidx : int64]  Index of the disjunctive constraint.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getdjcafeidxlist_LO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getdjcafeidxlist_LO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getdjcb_LO_3(self,djcidx,b):
      if b is None:
        raise TypeError("Argument b may not be None")
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",[0 for _ in range(len(b))])
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      _res_getdjcb,_retargs_getdjcb = self.__obj.getdjcb_LO_3(djcidx,memview_b)
      if _res_getdjcb != 0:
        _,_msg_getdjcb = self.__getlasterror(_res_getdjcb)
        raise Error(rescode(_res_getdjcb),_msg_getdjcb)
      if copyback_b:
        for __tmp_1282 in range(len(b)): b[__tmp_1282] = b_[__tmp_1282]
    def __getdjcb_LO_2(self,djcidx):
      b_ = bytearray(0)
      _res_getdjcb,_retargs_getdjcb = self.__obj.getdjcb_LO_2(djcidx,b_)
      if _res_getdjcb != 0:
        _,_msg_getdjcb = self.__getlasterror(_res_getdjcb)
        raise Error(rescode(_res_getdjcb),_msg_getdjcb)
      b = array.array("d")
      b.frombytes(b_)
      return (b)
    def getdjcb(self,*args,**kwds):
      """
      Obtains the optional constant term vector of a disjunctive constraint.
    
      getdjcb(djcidx,b)
      getdjcb(djcidx) -> (b)
        [b : array(float64)]  The vector b.  
        [djcidx : int64]  Index of the disjunctive constraint.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getdjcb_LO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getdjcb_LO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getdjctermsizelist_LO_3(self,djcidx,termsizelist):
      if termsizelist is None:
        raise TypeError("Argument termsizelist may not be None")
      copyback_termsizelist = False
      if termsizelist is None:
        termsizelist_ = None
        memview_termsizelist = None
      else:
        try:
          memview_termsizelist = memoryview(termsizelist)
        except TypeError:
          try:
            _tmparray_termsizelist = array.array("q",[0 for _ in range(len(termsizelist))])
          except TypeError:
            raise TypeError("Argument termsizelist has wrong type") from None
          else:
            memview_termsizelist = memoryview(_tmparray_termsizelist)
            copyback_termsizelist = True
            termsizelist_ = _tmparray_termsizelist
        else:
          if memview_termsizelist.ndim != 1:
            raise TypeError("Argument termsizelist must be one-dimensional")
          if memview_termsizelist.format != "q":
            _tmparray_termsizelist = array.array("q",termsizelist)
            memview_termsizelist = memoryview(_tmparray_termsizelist)
            copyback_termsizelist = True
            termsizelist_ = _tmparray_termsizelist
      _res_getdjctermsizelist,_retargs_getdjctermsizelist = self.__obj.getdjctermsizelist_LO_3(djcidx,memview_termsizelist)
      if _res_getdjctermsizelist != 0:
        _,_msg_getdjctermsizelist = self.__getlasterror(_res_getdjctermsizelist)
        raise Error(rescode(_res_getdjctermsizelist),_msg_getdjctermsizelist)
      if copyback_termsizelist:
        for __tmp_1288 in range(len(termsizelist)): termsizelist[__tmp_1288] = termsizelist_[__tmp_1288]
    def __getdjctermsizelist_LO_2(self,djcidx):
      termsizelist_ = bytearray(0)
      _res_getdjctermsizelist,_retargs_getdjctermsizelist = self.__obj.getdjctermsizelist_LO_2(djcidx,termsizelist_)
      if _res_getdjctermsizelist != 0:
        _,_msg_getdjctermsizelist = self.__getlasterror(_res_getdjctermsizelist)
        raise Error(rescode(_res_getdjctermsizelist),_msg_getdjctermsizelist)
      termsizelist = array.array("q")
      termsizelist.frombytes(termsizelist_)
      return (termsizelist)
    def getdjctermsizelist(self,*args,**kwds):
      """
      Obtains the list of term sizes in a disjunctive constraint.
    
      getdjctermsizelist(djcidx,termsizelist)
      getdjctermsizelist(djcidx) -> (termsizelist)
        [djcidx : int64]  Index of the disjunctive constraint.  
        [termsizelist : array(int64)]  List of term sizes.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getdjctermsizelist_LO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getdjctermsizelist_LO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getdjcs_OOOOO_6(self,domidxlist,afeidxlist,b,termsizelist,numterms):
      if domidxlist is None:
        raise TypeError("Argument domidxlist may not be None")
      copyback_domidxlist = False
      if domidxlist is None:
        domidxlist_ = None
        memview_domidxlist = None
      else:
        try:
          memview_domidxlist = memoryview(domidxlist)
        except TypeError:
          try:
            _tmparray_domidxlist = array.array("q",[0 for _ in range(len(domidxlist))])
          except TypeError:
            raise TypeError("Argument domidxlist has wrong type") from None
          else:
            memview_domidxlist = memoryview(_tmparray_domidxlist)
            copyback_domidxlist = True
            domidxlist_ = _tmparray_domidxlist
        else:
          if memview_domidxlist.ndim != 1:
            raise TypeError("Argument domidxlist must be one-dimensional")
          if memview_domidxlist.format != "q":
            _tmparray_domidxlist = array.array("q",domidxlist)
            memview_domidxlist = memoryview(_tmparray_domidxlist)
            copyback_domidxlist = True
            domidxlist_ = _tmparray_domidxlist
      if afeidxlist is None:
        raise TypeError("Argument afeidxlist may not be None")
      copyback_afeidxlist = False
      if afeidxlist is None:
        afeidxlist_ = None
        memview_afeidxlist = None
      else:
        try:
          memview_afeidxlist = memoryview(afeidxlist)
        except TypeError:
          try:
            _tmparray_afeidxlist = array.array("q",[0 for _ in range(len(afeidxlist))])
          except TypeError:
            raise TypeError("Argument afeidxlist has wrong type") from None
          else:
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
        else:
          if memview_afeidxlist.ndim != 1:
            raise TypeError("Argument afeidxlist must be one-dimensional")
          if memview_afeidxlist.format != "q":
            _tmparray_afeidxlist = array.array("q",afeidxlist)
            memview_afeidxlist = memoryview(_tmparray_afeidxlist)
            copyback_afeidxlist = True
            afeidxlist_ = _tmparray_afeidxlist
      if b is None:
        raise TypeError("Argument b may not be None")
      copyback_b = False
      if b is None:
        b_ = None
        memview_b = None
      else:
        try:
          memview_b = memoryview(b)
        except TypeError:
          try:
            _tmparray_b = array.array("d",[0 for _ in range(len(b))])
          except TypeError:
            raise TypeError("Argument b has wrong type") from None
          else:
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
        else:
          if memview_b.ndim != 1:
            raise TypeError("Argument b must be one-dimensional")
          if memview_b.format != "d":
            _tmparray_b = array.array("d",b)
            memview_b = memoryview(_tmparray_b)
            copyback_b = True
            b_ = _tmparray_b
      if termsizelist is None:
        raise TypeError("Argument termsizelist may not be None")
      copyback_termsizelist = False
      if termsizelist is None:
        termsizelist_ = None
        memview_termsizelist = None
      else:
        try:
          memview_termsizelist = memoryview(termsizelist)
        except TypeError:
          try:
            _tmparray_termsizelist = array.array("q",[0 for _ in range(len(termsizelist))])
          except TypeError:
            raise TypeError("Argument termsizelist has wrong type") from None
          else:
            memview_termsizelist = memoryview(_tmparray_termsizelist)
            copyback_termsizelist = True
            termsizelist_ = _tmparray_termsizelist
        else:
          if memview_termsizelist.ndim != 1:
            raise TypeError("Argument termsizelist must be one-dimensional")
          if memview_termsizelist.format != "q":
            _tmparray_termsizelist = array.array("q",termsizelist)
            memview_termsizelist = memoryview(_tmparray_termsizelist)
            copyback_termsizelist = True
            termsizelist_ = _tmparray_termsizelist
      if numterms is None:
        raise TypeError("Argument numterms may not be None")
      copyback_numterms = False
      if numterms is None:
        numterms_ = None
        memview_numterms = None
      else:
        try:
          memview_numterms = memoryview(numterms)
        except TypeError:
          try:
            _tmparray_numterms = array.array("q",[0 for _ in range(len(numterms))])
          except TypeError:
            raise TypeError("Argument numterms has wrong type") from None
          else:
            memview_numterms = memoryview(_tmparray_numterms)
            copyback_numterms = True
            numterms_ = _tmparray_numterms
        else:
          if memview_numterms.ndim != 1:
            raise TypeError("Argument numterms must be one-dimensional")
          if memview_numterms.format != "q":
            _tmparray_numterms = array.array("q",numterms)
            memview_numterms = memoryview(_tmparray_numterms)
            copyback_numterms = True
            numterms_ = _tmparray_numterms
      _res_getdjcs,_retargs_getdjcs = self.__obj.getdjcs_OOOOO_6(memview_domidxlist,memview_afeidxlist,memview_b,memview_termsizelist,memview_numterms)
      if _res_getdjcs != 0:
        _,_msg_getdjcs = self.__getlasterror(_res_getdjcs)
        raise Error(rescode(_res_getdjcs),_msg_getdjcs)
      if copyback_domidxlist:
        for __tmp_1294 in range(len(domidxlist)): domidxlist[__tmp_1294] = domidxlist_[__tmp_1294]
      if copyback_afeidxlist:
        for __tmp_1297 in range(len(afeidxlist)): afeidxlist[__tmp_1297] = afeidxlist_[__tmp_1297]
      if copyback_b:
        for __tmp_1300 in range(len(b)): b[__tmp_1300] = b_[__tmp_1300]
      if copyback_termsizelist:
        for __tmp_1303 in range(len(termsizelist)): termsizelist[__tmp_1303] = termsizelist_[__tmp_1303]
      if copyback_numterms:
        for __tmp_1306 in range(len(numterms)): numterms[__tmp_1306] = numterms_[__tmp_1306]
    def __getdjcs_OOOOO_1(self):
      domidxlist_ = bytearray(0)
      afeidxlist_ = bytearray(0)
      b_ = bytearray(0)
      termsizelist_ = bytearray(0)
      numterms_ = bytearray(0)
      _res_getdjcs,_retargs_getdjcs = self.__obj.getdjcs_OOOOO_1(domidxlist_,afeidxlist_,b_,termsizelist_,numterms_)
      if _res_getdjcs != 0:
        _,_msg_getdjcs = self.__getlasterror(_res_getdjcs)
        raise Error(rescode(_res_getdjcs),_msg_getdjcs)
      domidxlist = array.array("q")
      domidxlist.frombytes(domidxlist_)
      afeidxlist = array.array("q")
      afeidxlist.frombytes(afeidxlist_)
      b = array.array("d")
      b.frombytes(b_)
      termsizelist = array.array("q")
      termsizelist.frombytes(termsizelist_)
      numterms = array.array("q")
      numterms.frombytes(numterms_)
      return (domidxlist,afeidxlist,b,termsizelist,numterms)
    def getdjcs(self,*args,**kwds):
      """
      Obtains full data of all disjunctive constraints.
    
      getdjcs(domidxlist,
              afeidxlist,
              b,
              termsizelist,
              numterms)
      getdjcs() -> 
             (domidxlist,
              afeidxlist,
              b,
              termsizelist,
              numterms)
        [afeidxlist : array(int64)]  The concatenation of index lists of affine expressions appearing in all disjunctive constraints.  
        [b : array(float64)]  The concatenation of vectors b appearing in all disjunctive constraints.  
        [domidxlist : array(int64)]  The concatenation of index lists of domains appearing in all disjunctive constraints.  
        [numterms : array(int64)]  The number of terms in each of the disjunctive constraints.  
        [termsizelist : array(int64)]  The concatenation of lists of term sizes appearing in all disjunctive constraints.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__getdjcs_OOOOO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 1: return self.__getdjcs_OOOOO_1(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __putconbound_iidd_5(self,i,bkc,blc,buc):
      _res_putconbound,_retargs_putconbound = self.__obj.putconbound_iidd_5(i,bkc,blc,buc)
      if _res_putconbound != 0:
        _,_msg_putconbound = self.__getlasterror(_res_putconbound)
        raise Error(rescode(_res_putconbound),_msg_putconbound)
    def putconbound(self,*args,**kwds):
      """
      Changes the bound for one constraint.
    
      putconbound(i,bkc,blc,buc)
        [bkc : mosek.boundkey]  New bound key.  
        [blc : float64]  New lower bound.  
        [buc : float64]  New upper bound.  
        [i : int32]  Index of the constraint.  
      """
      return self.__putconbound_iidd_5(*args,**kwds)
    def __putconboundlist_OOOO_5(self,sub,bkc,blc,buc):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if bkc is None:
        bkc_ = None
      else:
        # i
        _tmparray_bkc_ = array.array("i",bkc)
        bkc_ = memoryview(_tmparray_bkc_)
      if blc is None:
        raise TypeError("Argument blc may not be None")
      copyback_blc = False
      if blc is None:
        blc_ = None
        memview_blc = None
      else:
        try:
          memview_blc = memoryview(blc)
        except TypeError:
          try:
            _tmparray_blc = array.array("d",blc)
          except TypeError:
            raise TypeError("Argument blc has wrong type") from None
          else:
            memview_blc = memoryview(_tmparray_blc)
            copyback_blc = True
            blc_ = _tmparray_blc
        else:
          if memview_blc.ndim != 1:
            raise TypeError("Argument blc must be one-dimensional")
          if memview_blc.format != "d":
            _tmparray_blc = array.array("d",blc)
            memview_blc = memoryview(_tmparray_blc)
            copyback_blc = True
            blc_ = _tmparray_blc
      if buc is None:
        raise TypeError("Argument buc may not be None")
      copyback_buc = False
      if buc is None:
        buc_ = None
        memview_buc = None
      else:
        try:
          memview_buc = memoryview(buc)
        except TypeError:
          try:
            _tmparray_buc = array.array("d",buc)
          except TypeError:
            raise TypeError("Argument buc has wrong type") from None
          else:
            memview_buc = memoryview(_tmparray_buc)
            copyback_buc = True
            buc_ = _tmparray_buc
        else:
          if memview_buc.ndim != 1:
            raise TypeError("Argument buc must be one-dimensional")
          if memview_buc.format != "d":
            _tmparray_buc = array.array("d",buc)
            memview_buc = memoryview(_tmparray_buc)
            copyback_buc = True
            buc_ = _tmparray_buc
      _res_putconboundlist,_retargs_putconboundlist = self.__obj.putconboundlist_OOOO_5(memview_sub,bkc_,memview_blc,memview_buc)
      if _res_putconboundlist != 0:
        _,_msg_putconboundlist = self.__getlasterror(_res_putconboundlist)
        raise Error(rescode(_res_putconboundlist),_msg_putconboundlist)
    def putconboundlist(self,*args,**kwds):
      """
      Changes the bounds of a list of constraints.
    
      putconboundlist(sub,bkc,blc,buc)
        [bkc : array(mosek.boundkey)]  Bound keys for the constraints.  
        [blc : array(float64)]  Lower bounds for the constraints.  
        [buc : array(float64)]  Upper bounds for the constraints.  
        [sub : array(int32)]  List of constraint indexes.  
      """
      return self.__putconboundlist_OOOO_5(*args,**kwds)
    def __putconboundlistconst_Oidd_5(self,sub,bkc,blc,buc):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      _res_putconboundlistconst,_retargs_putconboundlistconst = self.__obj.putconboundlistconst_Oidd_5(memview_sub,bkc,blc,buc)
      if _res_putconboundlistconst != 0:
        _,_msg_putconboundlistconst = self.__getlasterror(_res_putconboundlistconst)
        raise Error(rescode(_res_putconboundlistconst),_msg_putconboundlistconst)
    def putconboundlistconst(self,*args,**kwds):
      """
      Changes the bounds of a list of constraints.
    
      putconboundlistconst(sub,bkc,blc,buc)
        [bkc : mosek.boundkey]  New bound key for all constraints in the list.  
        [blc : float64]  New lower bound for all constraints in the list.  
        [buc : float64]  New upper bound for all constraints in the list.  
        [sub : array(int32)]  List of constraint indexes.  
      """
      return self.__putconboundlistconst_Oidd_5(*args,**kwds)
    def __putconboundslice_iiOOO_6(self,first,last,bkc,blc,buc):
      if bkc is None:
        bkc_ = None
      else:
        # i
        _tmparray_bkc_ = array.array("i",bkc)
        bkc_ = memoryview(_tmparray_bkc_)
      if blc is None:
        raise TypeError("Argument blc may not be None")
      copyback_blc = False
      if blc is None:
        blc_ = None
        memview_blc = None
      else:
        try:
          memview_blc = memoryview(blc)
        except TypeError:
          try:
            _tmparray_blc = array.array("d",blc)
          except TypeError:
            raise TypeError("Argument blc has wrong type") from None
          else:
            memview_blc = memoryview(_tmparray_blc)
            copyback_blc = True
            blc_ = _tmparray_blc
        else:
          if memview_blc.ndim != 1:
            raise TypeError("Argument blc must be one-dimensional")
          if memview_blc.format != "d":
            _tmparray_blc = array.array("d",blc)
            memview_blc = memoryview(_tmparray_blc)
            copyback_blc = True
            blc_ = _tmparray_blc
      if buc is None:
        raise TypeError("Argument buc may not be None")
      copyback_buc = False
      if buc is None:
        buc_ = None
        memview_buc = None
      else:
        try:
          memview_buc = memoryview(buc)
        except TypeError:
          try:
            _tmparray_buc = array.array("d",buc)
          except TypeError:
            raise TypeError("Argument buc has wrong type") from None
          else:
            memview_buc = memoryview(_tmparray_buc)
            copyback_buc = True
            buc_ = _tmparray_buc
        else:
          if memview_buc.ndim != 1:
            raise TypeError("Argument buc must be one-dimensional")
          if memview_buc.format != "d":
            _tmparray_buc = array.array("d",buc)
            memview_buc = memoryview(_tmparray_buc)
            copyback_buc = True
            buc_ = _tmparray_buc
      _res_putconboundslice,_retargs_putconboundslice = self.__obj.putconboundslice_iiOOO_6(first,last,bkc_,memview_blc,memview_buc)
      if _res_putconboundslice != 0:
        _,_msg_putconboundslice = self.__getlasterror(_res_putconboundslice)
        raise Error(rescode(_res_putconboundslice),_msg_putconboundslice)
    def putconboundslice(self,*args,**kwds):
      """
      Changes the bounds for a slice of the constraints.
    
      putconboundslice(first,last,bkc,blc,buc)
        [bkc : array(mosek.boundkey)]  Bound keys for the constraints.  
        [blc : array(float64)]  Lower bounds for the constraints.  
        [buc : array(float64)]  Upper bounds for the constraints.  
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
      """
      return self.__putconboundslice_iiOOO_6(*args,**kwds)
    def __putconboundsliceconst_iiidd_6(self,first,last,bkc,blc,buc):
      _res_putconboundsliceconst,_retargs_putconboundsliceconst = self.__obj.putconboundsliceconst_iiidd_6(first,last,bkc,blc,buc)
      if _res_putconboundsliceconst != 0:
        _,_msg_putconboundsliceconst = self.__getlasterror(_res_putconboundsliceconst)
        raise Error(rescode(_res_putconboundsliceconst),_msg_putconboundsliceconst)
    def putconboundsliceconst(self,*args,**kwds):
      """
      Changes the bounds for a slice of the constraints.
    
      putconboundsliceconst(first,last,bkc,blc,buc)
        [bkc : mosek.boundkey]  New bound key for all constraints in the slice.  
        [blc : float64]  New lower bound for all constraints in the slice.  
        [buc : float64]  New upper bound for all constraints in the slice.  
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
      """
      return self.__putconboundsliceconst_iiidd_6(*args,**kwds)
    def __putvarbound_iidd_5(self,j,bkx,blx,bux):
      _res_putvarbound,_retargs_putvarbound = self.__obj.putvarbound_iidd_5(j,bkx,blx,bux)
      if _res_putvarbound != 0:
        _,_msg_putvarbound = self.__getlasterror(_res_putvarbound)
        raise Error(rescode(_res_putvarbound),_msg_putvarbound)
    def putvarbound(self,*args,**kwds):
      """
      Changes the bounds for one variable.
    
      putvarbound(j,bkx,blx,bux)
        [bkx : mosek.boundkey]  New bound key.  
        [blx : float64]  New lower bound.  
        [bux : float64]  New upper bound.  
        [j : int32]  Index of the variable.  
      """
      return self.__putvarbound_iidd_5(*args,**kwds)
    def __putvarboundlist_OOOO_5(self,sub,bkx,blx,bux):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if bkx is None:
        bkx_ = None
      else:
        # i
        _tmparray_bkx_ = array.array("i",bkx)
        bkx_ = memoryview(_tmparray_bkx_)
      if blx is None:
        raise TypeError("Argument blx may not be None")
      copyback_blx = False
      if blx is None:
        blx_ = None
        memview_blx = None
      else:
        try:
          memview_blx = memoryview(blx)
        except TypeError:
          try:
            _tmparray_blx = array.array("d",blx)
          except TypeError:
            raise TypeError("Argument blx has wrong type") from None
          else:
            memview_blx = memoryview(_tmparray_blx)
            copyback_blx = True
            blx_ = _tmparray_blx
        else:
          if memview_blx.ndim != 1:
            raise TypeError("Argument blx must be one-dimensional")
          if memview_blx.format != "d":
            _tmparray_blx = array.array("d",blx)
            memview_blx = memoryview(_tmparray_blx)
            copyback_blx = True
            blx_ = _tmparray_blx
      if bux is None:
        raise TypeError("Argument bux may not be None")
      copyback_bux = False
      if bux is None:
        bux_ = None
        memview_bux = None
      else:
        try:
          memview_bux = memoryview(bux)
        except TypeError:
          try:
            _tmparray_bux = array.array("d",bux)
          except TypeError:
            raise TypeError("Argument bux has wrong type") from None
          else:
            memview_bux = memoryview(_tmparray_bux)
            copyback_bux = True
            bux_ = _tmparray_bux
        else:
          if memview_bux.ndim != 1:
            raise TypeError("Argument bux must be one-dimensional")
          if memview_bux.format != "d":
            _tmparray_bux = array.array("d",bux)
            memview_bux = memoryview(_tmparray_bux)
            copyback_bux = True
            bux_ = _tmparray_bux
      _res_putvarboundlist,_retargs_putvarboundlist = self.__obj.putvarboundlist_OOOO_5(memview_sub,bkx_,memview_blx,memview_bux)
      if _res_putvarboundlist != 0:
        _,_msg_putvarboundlist = self.__getlasterror(_res_putvarboundlist)
        raise Error(rescode(_res_putvarboundlist),_msg_putvarboundlist)
    def putvarboundlist(self,*args,**kwds):
      """
      Changes the bounds of a list of variables.
    
      putvarboundlist(sub,bkx,blx,bux)
        [bkx : array(mosek.boundkey)]  Bound keys for the variables.  
        [blx : array(float64)]  Lower bounds for the variables.  
        [bux : array(float64)]  Upper bounds for the variables.  
        [sub : array(int32)]  List of variable indexes.  
      """
      return self.__putvarboundlist_OOOO_5(*args,**kwds)
    def __putvarboundlistconst_Oidd_5(self,sub,bkx,blx,bux):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("i",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "i":
            _tmparray_sub = array.array("i",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      _res_putvarboundlistconst,_retargs_putvarboundlistconst = self.__obj.putvarboundlistconst_Oidd_5(memview_sub,bkx,blx,bux)
      if _res_putvarboundlistconst != 0:
        _,_msg_putvarboundlistconst = self.__getlasterror(_res_putvarboundlistconst)
        raise Error(rescode(_res_putvarboundlistconst),_msg_putvarboundlistconst)
    def putvarboundlistconst(self,*args,**kwds):
      """
      Changes the bounds of a list of variables.
    
      putvarboundlistconst(sub,bkx,blx,bux)
        [bkx : mosek.boundkey]  New bound key for all variables in the list.  
        [blx : float64]  New lower bound for all variables in the list.  
        [bux : float64]  New upper bound for all variables in the list.  
        [sub : array(int32)]  List of variable indexes.  
      """
      return self.__putvarboundlistconst_Oidd_5(*args,**kwds)
    def __putvarboundslice_iiOOO_6(self,first,last,bkx,blx,bux):
      if bkx is None:
        bkx_ = None
      else:
        # i
        _tmparray_bkx_ = array.array("i",bkx)
        bkx_ = memoryview(_tmparray_bkx_)
      if blx is None:
        raise TypeError("Argument blx may not be None")
      copyback_blx = False
      if blx is None:
        blx_ = None
        memview_blx = None
      else:
        try:
          memview_blx = memoryview(blx)
        except TypeError:
          try:
            _tmparray_blx = array.array("d",blx)
          except TypeError:
            raise TypeError("Argument blx has wrong type") from None
          else:
            memview_blx = memoryview(_tmparray_blx)
            copyback_blx = True
            blx_ = _tmparray_blx
        else:
          if memview_blx.ndim != 1:
            raise TypeError("Argument blx must be one-dimensional")
          if memview_blx.format != "d":
            _tmparray_blx = array.array("d",blx)
            memview_blx = memoryview(_tmparray_blx)
            copyback_blx = True
            blx_ = _tmparray_blx
      if bux is None:
        raise TypeError("Argument bux may not be None")
      copyback_bux = False
      if bux is None:
        bux_ = None
        memview_bux = None
      else:
        try:
          memview_bux = memoryview(bux)
        except TypeError:
          try:
            _tmparray_bux = array.array("d",bux)
          except TypeError:
            raise TypeError("Argument bux has wrong type") from None
          else:
            memview_bux = memoryview(_tmparray_bux)
            copyback_bux = True
            bux_ = _tmparray_bux
        else:
          if memview_bux.ndim != 1:
            raise TypeError("Argument bux must be one-dimensional")
          if memview_bux.format != "d":
            _tmparray_bux = array.array("d",bux)
            memview_bux = memoryview(_tmparray_bux)
            copyback_bux = True
            bux_ = _tmparray_bux
      _res_putvarboundslice,_retargs_putvarboundslice = self.__obj.putvarboundslice_iiOOO_6(first,last,bkx_,memview_blx,memview_bux)
      if _res_putvarboundslice != 0:
        _,_msg_putvarboundslice = self.__getlasterror(_res_putvarboundslice)
        raise Error(rescode(_res_putvarboundslice),_msg_putvarboundslice)
    def putvarboundslice(self,*args,**kwds):
      """
      Changes the bounds for a slice of the variables.
    
      putvarboundslice(first,last,bkx,blx,bux)
        [bkx : array(mosek.boundkey)]  Bound keys for the variables.  
        [blx : array(float64)]  Lower bounds for the variables.  
        [bux : array(float64)]  Upper bounds for the variables.  
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
      """
      return self.__putvarboundslice_iiOOO_6(*args,**kwds)
    def __putvarboundsliceconst_iiidd_6(self,first,last,bkx,blx,bux):
      _res_putvarboundsliceconst,_retargs_putvarboundsliceconst = self.__obj.putvarboundsliceconst_iiidd_6(first,last,bkx,blx,bux)
      if _res_putvarboundsliceconst != 0:
        _,_msg_putvarboundsliceconst = self.__getlasterror(_res_putvarboundsliceconst)
        raise Error(rescode(_res_putvarboundsliceconst),_msg_putvarboundsliceconst)
    def putvarboundsliceconst(self,*args,**kwds):
      """
      Changes the bounds for a slice of the variables.
    
      putvarboundsliceconst(first,last,bkx,blx,bux)
        [bkx : mosek.boundkey]  New bound key for all variables in the slice.  
        [blx : float64]  New lower bound for all variables in the slice.  
        [bux : float64]  New upper bound for all variables in the slice.  
        [first : int32]  First index in the sequence.  
        [last : int32]  Last index plus 1 in the sequence.  
      """
      return self.__putvarboundsliceconst_iiidd_6(*args,**kwds)
    def __putcfix_d_2(self,cfix):
      _res_putcfix,_retargs_putcfix = self.__obj.putcfix_d_2(cfix)
      if _res_putcfix != 0:
        _,_msg_putcfix = self.__getlasterror(_res_putcfix)
        raise Error(rescode(_res_putcfix),_msg_putcfix)
    def putcfix(self,*args,**kwds):
      """
      Replaces the fixed term in the objective.
    
      putcfix(cfix)
        [cfix : float64]  Fixed term in the objective.  
      """
      return self.__putcfix_d_2(*args,**kwds)
    def __putcj_id_3(self,j,cj):
      _res_putcj,_retargs_putcj = self.__obj.putcj_id_3(j,cj)
      if _res_putcj != 0:
        _,_msg_putcj = self.__getlasterror(_res_putcj)
        raise Error(rescode(_res_putcj),_msg_putcj)
    def putcj(self,*args,**kwds):
      """
      Modifies one linear coefficient in the objective.
    
      putcj(j,cj)
        [cj : float64]  New coefficient value.  
        [j : int32]  Index of the variable whose objective coefficient should be changed.  
      """
      return self.__putcj_id_3(*args,**kwds)
    def __putobjsense_i_2(self,sense):
      _res_putobjsense,_retargs_putobjsense = self.__obj.putobjsense_i_2(sense)
      if _res_putobjsense != 0:
        _,_msg_putobjsense = self.__getlasterror(_res_putobjsense)
        raise Error(rescode(_res_putobjsense),_msg_putobjsense)
    def putobjsense(self,*args,**kwds):
      """
      Sets the objective sense.
    
      putobjsense(sense)
        [sense : mosek.objsense]  The objective sense of the task  
      """
      return self.__putobjsense_i_2(*args,**kwds)
    def __getobjsense__1(self):
      _res_getobjsense,_retargs_getobjsense = self.__obj.getobjsense__1()
      if _res_getobjsense != 0:
        _,_msg_getobjsense = self.__getlasterror(_res_getobjsense)
        raise Error(rescode(_res_getobjsense),_msg_getobjsense)
      else:
        (sense) = _retargs_getobjsense
      return (objsense(sense))
    def getobjsense(self,*args,**kwds):
      """
      Gets the objective sense.
    
      getobjsense() -> (sense)
        [sense : mosek.objsense]  The returned objective sense.  
      """
      return self.__getobjsense__1(*args,**kwds)
    def __putclist_OO_3(self,subj,val):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if val is None:
        raise TypeError("Argument val may not be None")
      copyback_val = False
      if val is None:
        val_ = None
        memview_val = None
      else:
        try:
          memview_val = memoryview(val)
        except TypeError:
          try:
            _tmparray_val = array.array("d",val)
          except TypeError:
            raise TypeError("Argument val has wrong type") from None
          else:
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
        else:
          if memview_val.ndim != 1:
            raise TypeError("Argument val must be one-dimensional")
          if memview_val.format != "d":
            _tmparray_val = array.array("d",val)
            memview_val = memoryview(_tmparray_val)
            copyback_val = True
            val_ = _tmparray_val
      _res_putclist,_retargs_putclist = self.__obj.putclist_OO_3(memview_subj,memview_val)
      if _res_putclist != 0:
        _,_msg_putclist = self.__getlasterror(_res_putclist)
        raise Error(rescode(_res_putclist),_msg_putclist)
    def putclist(self,*args,**kwds):
      """
      Modifies a part of the linear objective coefficients.
    
      putclist(subj,val)
        [subj : array(int32)]  Indices of variables for which objective coefficients should be changed.  
        [val : array(float64)]  New numerical values for the objective coefficients that should be modified.  
      """
      return self.__putclist_OO_3(*args,**kwds)
    def __putcslice_iiO_4(self,first,last,slice):
      if slice is None:
        raise TypeError("Argument slice may not be None")
      copyback_slice = False
      if slice is None:
        slice_ = None
        memview_slice = None
      else:
        try:
          memview_slice = memoryview(slice)
        except TypeError:
          try:
            _tmparray_slice = array.array("d",slice)
          except TypeError:
            raise TypeError("Argument slice has wrong type") from None
          else:
            memview_slice = memoryview(_tmparray_slice)
            copyback_slice = True
            slice_ = _tmparray_slice
        else:
          if memview_slice.ndim != 1:
            raise TypeError("Argument slice must be one-dimensional")
          if memview_slice.format != "d":
            _tmparray_slice = array.array("d",slice)
            memview_slice = memoryview(_tmparray_slice)
            copyback_slice = True
            slice_ = _tmparray_slice
      _res_putcslice,_retargs_putcslice = self.__obj.putcslice_iiO_4(first,last,memview_slice)
      if _res_putcslice != 0:
        _,_msg_putcslice = self.__getlasterror(_res_putcslice)
        raise Error(rescode(_res_putcslice),_msg_putcslice)
    def putcslice(self,*args,**kwds):
      """
      Modifies a slice of the linear objective coefficients.
    
      putcslice(first,last,slice)
        [first : int32]  First element in the slice of c.  
        [last : int32]  Last element plus 1 of the slice in c to be changed.  
        [slice : array(float64)]  New numerical values for the objective coefficients that should be modified.  
      """
      return self.__putcslice_iiO_4(*args,**kwds)
    def __putbarcj_iOO_4(self,j,sub,weights):
      if sub is None:
        raise TypeError("Argument sub may not be None")
      copyback_sub = False
      if sub is None:
        sub_ = None
        memview_sub = None
      else:
        try:
          memview_sub = memoryview(sub)
        except TypeError:
          try:
            _tmparray_sub = array.array("q",sub)
          except TypeError:
            raise TypeError("Argument sub has wrong type") from None
          else:
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
        else:
          if memview_sub.ndim != 1:
            raise TypeError("Argument sub must be one-dimensional")
          if memview_sub.format != "q":
            _tmparray_sub = array.array("q",sub)
            memview_sub = memoryview(_tmparray_sub)
            copyback_sub = True
            sub_ = _tmparray_sub
      if weights is None:
        raise TypeError("Argument weights may not be None")
      copyback_weights = False
      if weights is None:
        weights_ = None
        memview_weights = None
      else:
        try:
          memview_weights = memoryview(weights)
        except TypeError:
          try:
            _tmparray_weights = array.array("d",weights)
          except TypeError:
            raise TypeError("Argument weights has wrong type") from None
          else:
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
        else:
          if memview_weights.ndim != 1:
            raise TypeError("Argument weights must be one-dimensional")
          if memview_weights.format != "d":
            _tmparray_weights = array.array("d",weights)
            memview_weights = memoryview(_tmparray_weights)
            copyback_weights = True
            weights_ = _tmparray_weights
      _res_putbarcj,_retargs_putbarcj = self.__obj.putbarcj_iOO_4(j,memview_sub,memview_weights)
      if _res_putbarcj != 0:
        _,_msg_putbarcj = self.__getlasterror(_res_putbarcj)
        raise Error(rescode(_res_putbarcj),_msg_putbarcj)
    def putbarcj(self,*args,**kwds):
      """
      Changes one element in barc.
    
      putbarcj(j,sub,weights)
        [j : int32]  Index of the element in barc` that should be changed.  
        [sub : array(int64)]  sub is list of indexes of those symmetric matrices appearing in sum.  
        [weights : array(float64)]  The weights of the terms in the weighted sum.  
      """
      return self.__putbarcj_iOO_4(*args,**kwds)
    def __putcone_iidO_5(self,k,ct,conepar,submem):
      if submem is None:
        raise TypeError("Argument submem may not be None")
      copyback_submem = False
      if submem is None:
        submem_ = None
        memview_submem = None
      else:
        try:
          memview_submem = memoryview(submem)
        except TypeError:
          try:
            _tmparray_submem = array.array("i",submem)
          except TypeError:
            raise TypeError("Argument submem has wrong type") from None
          else:
            memview_submem = memoryview(_tmparray_submem)
            copyback_submem = True
            submem_ = _tmparray_submem
        else:
          if memview_submem.ndim != 1:
            raise TypeError("Argument submem must be one-dimensional")
          if memview_submem.format != "i":
            _tmparray_submem = array.array("i",submem)
            memview_submem = memoryview(_tmparray_submem)
            copyback_submem = True
            submem_ = _tmparray_submem
      _res_putcone,_retargs_putcone = self.__obj.putcone_iidO_5(k,ct,conepar,memview_submem)
      if _res_putcone != 0:
        _,_msg_putcone = self.__getlasterror(_res_putcone)
        raise Error(rescode(_res_putcone),_msg_putcone)
    def putcone(self,*args,**kwds):
      """
      Replaces a conic constraint.
    
      putcone(k,ct,conepar,submem)
        [conepar : float64]  For the power cone it denotes the exponent alpha. For other cone types it is unused and can be set to 0.  
        [ct : mosek.conetype]  Specifies the type of the cone.  
        [k : int32]  Index of the cone.  
        [submem : array(int32)]  Variable subscripts of the members in the cone.  
      """
      return self.__putcone_iidO_5(*args,**kwds)
    def __putmaxnumdomain_L_2(self,maxnumdomain):
      _res_putmaxnumdomain,_retargs_putmaxnumdomain = self.__obj.putmaxnumdomain_L_2(maxnumdomain)
      if _res_putmaxnumdomain != 0:
        _,_msg_putmaxnumdomain = self.__getlasterror(_res_putmaxnumdomain)
        raise Error(rescode(_res_putmaxnumdomain),_msg_putmaxnumdomain)
    def putmaxnumdomain(self,*args,**kwds):
      """
      Sets the number of preallocated domains in the optimization task.
    
      putmaxnumdomain(maxnumdomain)
        [maxnumdomain : int64]  Number of preallocated domains.  
      """
      return self.__putmaxnumdomain_L_2(*args,**kwds)
    def __getnumdomain__1(self):
      _res_getnumdomain,_retargs_getnumdomain = self.__obj.getnumdomain__1()
      if _res_getnumdomain != 0:
        _,_msg_getnumdomain = self.__getlasterror(_res_getnumdomain)
        raise Error(rescode(_res_getnumdomain),_msg_getnumdomain)
      else:
        (numdomain) = _retargs_getnumdomain
      return (numdomain)
    def getnumdomain(self,*args,**kwds):
      """
      Obtain the number of domains defined.
    
      getnumdomain() -> (numdomain)
        [numdomain : int64]  Number of domains in the task.  
      """
      return self.__getnumdomain__1(*args,**kwds)
    def __appendrplusdomain_L_2(self,n):
      _res_appendrplusdomain,_retargs_appendrplusdomain = self.__obj.appendrplusdomain_L_2(n)
      if _res_appendrplusdomain != 0:
        _,_msg_appendrplusdomain = self.__getlasterror(_res_appendrplusdomain)
        raise Error(rescode(_res_appendrplusdomain),_msg_appendrplusdomain)
      else:
        (domidx) = _retargs_appendrplusdomain
      return (domidx)
    def appendrplusdomain(self,*args,**kwds):
      """
      Appends the n dimensional positive orthant to the list of domains.
    
      appendrplusdomain(n) -> (domidx)
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimmension of the domain.  
      """
      return self.__appendrplusdomain_L_2(*args,**kwds)
    def __appendrminusdomain_L_2(self,n):
      _res_appendrminusdomain,_retargs_appendrminusdomain = self.__obj.appendrminusdomain_L_2(n)
      if _res_appendrminusdomain != 0:
        _,_msg_appendrminusdomain = self.__getlasterror(_res_appendrminusdomain)
        raise Error(rescode(_res_appendrminusdomain),_msg_appendrminusdomain)
      else:
        (domidx) = _retargs_appendrminusdomain
      return (domidx)
    def appendrminusdomain(self,*args,**kwds):
      """
      Appends the n dimensional negative orthant to the list of domains.
    
      appendrminusdomain(n) -> (domidx)
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimmension of the domain.  
      """
      return self.__appendrminusdomain_L_2(*args,**kwds)
    def __appendrdomain_L_2(self,n):
      _res_appendrdomain,_retargs_appendrdomain = self.__obj.appendrdomain_L_2(n)
      if _res_appendrdomain != 0:
        _,_msg_appendrdomain = self.__getlasterror(_res_appendrdomain)
        raise Error(rescode(_res_appendrdomain),_msg_appendrdomain)
      else:
        (domidx) = _retargs_appendrdomain
      return (domidx)
    def appendrdomain(self,*args,**kwds):
      """
      Appends the n dimensional real number domain.
    
      appendrdomain(n) -> (domidx)
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimmension of the domain.  
      """
      return self.__appendrdomain_L_2(*args,**kwds)
    def __appendrzerodomain_L_2(self,n):
      _res_appendrzerodomain,_retargs_appendrzerodomain = self.__obj.appendrzerodomain_L_2(n)
      if _res_appendrzerodomain != 0:
        _,_msg_appendrzerodomain = self.__getlasterror(_res_appendrzerodomain)
        raise Error(rescode(_res_appendrzerodomain),_msg_appendrzerodomain)
      else:
        (domidx) = _retargs_appendrzerodomain
      return (domidx)
    def appendrzerodomain(self,*args,**kwds):
      """
      Appends the n dimensional 0 domain.
    
      appendrzerodomain(n) -> (domidx)
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimmension of the domain.  
      """
      return self.__appendrzerodomain_L_2(*args,**kwds)
    def __appendquadraticconedomain_L_2(self,n):
      _res_appendquadraticconedomain,_retargs_appendquadraticconedomain = self.__obj.appendquadraticconedomain_L_2(n)
      if _res_appendquadraticconedomain != 0:
        _,_msg_appendquadraticconedomain = self.__getlasterror(_res_appendquadraticconedomain)
        raise Error(rescode(_res_appendquadraticconedomain),_msg_appendquadraticconedomain)
      else:
        (domidx) = _retargs_appendquadraticconedomain
      return (domidx)
    def appendquadraticconedomain(self,*args,**kwds):
      """
      Appends the n dimensional quadratic cone domain.
    
      appendquadraticconedomain(n) -> (domidx)
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimmension of the domain.  
      """
      return self.__appendquadraticconedomain_L_2(*args,**kwds)
    def __appendrquadraticconedomain_L_2(self,n):
      _res_appendrquadraticconedomain,_retargs_appendrquadraticconedomain = self.__obj.appendrquadraticconedomain_L_2(n)
      if _res_appendrquadraticconedomain != 0:
        _,_msg_appendrquadraticconedomain = self.__getlasterror(_res_appendrquadraticconedomain)
        raise Error(rescode(_res_appendrquadraticconedomain),_msg_appendrquadraticconedomain)
      else:
        (domidx) = _retargs_appendrquadraticconedomain
      return (domidx)
    def appendrquadraticconedomain(self,*args,**kwds):
      """
      Appends the n dimensional rotated quadratic cone domain.
    
      appendrquadraticconedomain(n) -> (domidx)
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimmension of the domain.  
      """
      return self.__appendrquadraticconedomain_L_2(*args,**kwds)
    def __appendprimalexpconedomain__1(self):
      _res_appendprimalexpconedomain,_retargs_appendprimalexpconedomain = self.__obj.appendprimalexpconedomain__1()
      if _res_appendprimalexpconedomain != 0:
        _,_msg_appendprimalexpconedomain = self.__getlasterror(_res_appendprimalexpconedomain)
        raise Error(rescode(_res_appendprimalexpconedomain),_msg_appendprimalexpconedomain)
      else:
        (domidx) = _retargs_appendprimalexpconedomain
      return (domidx)
    def appendprimalexpconedomain(self,*args,**kwds):
      """
      Appends the primal exponential cone domain.
    
      appendprimalexpconedomain() -> (domidx)
        [domidx : int64]  Index of the domain.  
      """
      return self.__appendprimalexpconedomain__1(*args,**kwds)
    def __appenddualexpconedomain__1(self):
      _res_appenddualexpconedomain,_retargs_appenddualexpconedomain = self.__obj.appenddualexpconedomain__1()
      if _res_appenddualexpconedomain != 0:
        _,_msg_appenddualexpconedomain = self.__getlasterror(_res_appenddualexpconedomain)
        raise Error(rescode(_res_appenddualexpconedomain),_msg_appenddualexpconedomain)
      else:
        (domidx) = _retargs_appenddualexpconedomain
      return (domidx)
    def appenddualexpconedomain(self,*args,**kwds):
      """
      Appends the dual exponential cone domain.
    
      appenddualexpconedomain() -> (domidx)
        [domidx : int64]  Index of the domain.  
      """
      return self.__appenddualexpconedomain__1(*args,**kwds)
    def __appendprimalgeomeanconedomain_L_2(self,n):
      _res_appendprimalgeomeanconedomain,_retargs_appendprimalgeomeanconedomain = self.__obj.appendprimalgeomeanconedomain_L_2(n)
      if _res_appendprimalgeomeanconedomain != 0:
        _,_msg_appendprimalgeomeanconedomain = self.__getlasterror(_res_appendprimalgeomeanconedomain)
        raise Error(rescode(_res_appendprimalgeomeanconedomain),_msg_appendprimalgeomeanconedomain)
      else:
        (domidx) = _retargs_appendprimalgeomeanconedomain
      return (domidx)
    def appendprimalgeomeanconedomain(self,*args,**kwds):
      """
      Appends the primal geometric mean cone domain.
    
      appendprimalgeomeanconedomain(n) -> (domidx)
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimmension of the domain.  
      """
      return self.__appendprimalgeomeanconedomain_L_2(*args,**kwds)
    def __appenddualgeomeanconedomain_L_2(self,n):
      _res_appenddualgeomeanconedomain,_retargs_appenddualgeomeanconedomain = self.__obj.appenddualgeomeanconedomain_L_2(n)
      if _res_appenddualgeomeanconedomain != 0:
        _,_msg_appenddualgeomeanconedomain = self.__getlasterror(_res_appenddualgeomeanconedomain)
        raise Error(rescode(_res_appenddualgeomeanconedomain),_msg_appenddualgeomeanconedomain)
      else:
        (domidx) = _retargs_appenddualgeomeanconedomain
      return (domidx)
    def appenddualgeomeanconedomain(self,*args,**kwds):
      """
      Appends the dual geometric mean cone domain.
    
      appenddualgeomeanconedomain(n) -> (domidx)
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimmension of the domain.  
      """
      return self.__appenddualgeomeanconedomain_L_2(*args,**kwds)
    def __appendprimalpowerconedomain_LO_3(self,n,alpha):
      if alpha is None:
        raise TypeError("Argument alpha may not be None")
      copyback_alpha = False
      if alpha is None:
        alpha_ = None
        memview_alpha = None
      else:
        try:
          memview_alpha = memoryview(alpha)
        except TypeError:
          try:
            _tmparray_alpha = array.array("d",alpha)
          except TypeError:
            raise TypeError("Argument alpha has wrong type") from None
          else:
            memview_alpha = memoryview(_tmparray_alpha)
            copyback_alpha = True
            alpha_ = _tmparray_alpha
        else:
          if memview_alpha.ndim != 1:
            raise TypeError("Argument alpha must be one-dimensional")
          if memview_alpha.format != "d":
            _tmparray_alpha = array.array("d",alpha)
            memview_alpha = memoryview(_tmparray_alpha)
            copyback_alpha = True
            alpha_ = _tmparray_alpha
      _res_appendprimalpowerconedomain,_retargs_appendprimalpowerconedomain = self.__obj.appendprimalpowerconedomain_LO_3(n,memview_alpha)
      if _res_appendprimalpowerconedomain != 0:
        _,_msg_appendprimalpowerconedomain = self.__getlasterror(_res_appendprimalpowerconedomain)
        raise Error(rescode(_res_appendprimalpowerconedomain),_msg_appendprimalpowerconedomain)
      else:
        (domidx) = _retargs_appendprimalpowerconedomain
      return (domidx)
    def appendprimalpowerconedomain(self,*args,**kwds):
      """
      Appends the primal power cone domain.
    
      appendprimalpowerconedomain(n,alpha) -> (domidx)
        [alpha : array(float64)]  The sequence proportional to exponents. Must be positive.  
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimension of the domain.  
      """
      return self.__appendprimalpowerconedomain_LO_3(*args,**kwds)
    def __appenddualpowerconedomain_LO_3(self,n,alpha):
      if alpha is None:
        raise TypeError("Argument alpha may not be None")
      copyback_alpha = False
      if alpha is None:
        alpha_ = None
        memview_alpha = None
      else:
        try:
          memview_alpha = memoryview(alpha)
        except TypeError:
          try:
            _tmparray_alpha = array.array("d",alpha)
          except TypeError:
            raise TypeError("Argument alpha has wrong type") from None
          else:
            memview_alpha = memoryview(_tmparray_alpha)
            copyback_alpha = True
            alpha_ = _tmparray_alpha
        else:
          if memview_alpha.ndim != 1:
            raise TypeError("Argument alpha must be one-dimensional")
          if memview_alpha.format != "d":
            _tmparray_alpha = array.array("d",alpha)
            memview_alpha = memoryview(_tmparray_alpha)
            copyback_alpha = True
            alpha_ = _tmparray_alpha
      _res_appenddualpowerconedomain,_retargs_appenddualpowerconedomain = self.__obj.appenddualpowerconedomain_LO_3(n,memview_alpha)
      if _res_appenddualpowerconedomain != 0:
        _,_msg_appenddualpowerconedomain = self.__getlasterror(_res_appenddualpowerconedomain)
        raise Error(rescode(_res_appenddualpowerconedomain),_msg_appenddualpowerconedomain)
      else:
        (domidx) = _retargs_appenddualpowerconedomain
      return (domidx)
    def appenddualpowerconedomain(self,*args,**kwds):
      """
      Appends the dual power cone domain.
    
      appenddualpowerconedomain(n,alpha) -> (domidx)
        [alpha : array(float64)]  The sequence proportional to exponents. Must be positive.  
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimension of the domain.  
      """
      return self.__appenddualpowerconedomain_LO_3(*args,**kwds)
    def __appendsvecpsdconedomain_L_2(self,n):
      _res_appendsvecpsdconedomain,_retargs_appendsvecpsdconedomain = self.__obj.appendsvecpsdconedomain_L_2(n)
      if _res_appendsvecpsdconedomain != 0:
        _,_msg_appendsvecpsdconedomain = self.__getlasterror(_res_appendsvecpsdconedomain)
        raise Error(rescode(_res_appendsvecpsdconedomain),_msg_appendsvecpsdconedomain)
      else:
        (domidx) = _retargs_appendsvecpsdconedomain
      return (domidx)
    def appendsvecpsdconedomain(self,*args,**kwds):
      """
      Appends the vectorized SVEC PSD cone domain.
    
      appendsvecpsdconedomain(n) -> (domidx)
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimension of the domain.  
      """
      return self.__appendsvecpsdconedomain_L_2(*args,**kwds)
    def __getdomaintype_L_2(self,domidx):
      _res_getdomaintype,_retargs_getdomaintype = self.__obj.getdomaintype_L_2(domidx)
      if _res_getdomaintype != 0:
        _,_msg_getdomaintype = self.__getlasterror(_res_getdomaintype)
        raise Error(rescode(_res_getdomaintype),_msg_getdomaintype)
      else:
        (domtype) = _retargs_getdomaintype
      return (domaintype(domtype))
    def getdomaintype(self,*args,**kwds):
      """
      Returns the type of the domain.
    
      getdomaintype(domidx) -> (domtype)
        [domidx : int64]  Index of the domain.  
        [domtype : mosek.domaintype]  The type of the domain.  
      """
      return self.__getdomaintype_L_2(*args,**kwds)
    def __getdomainn_L_2(self,domidx):
      _res_getdomainn,_retargs_getdomainn = self.__obj.getdomainn_L_2(domidx)
      if _res_getdomainn != 0:
        _,_msg_getdomainn = self.__getlasterror(_res_getdomainn)
        raise Error(rescode(_res_getdomainn),_msg_getdomainn)
      else:
        (n) = _retargs_getdomainn
      return (n)
    def getdomainn(self,*args,**kwds):
      """
      Obtains the dimension of the domain.
    
      getdomainn(domidx) -> (n)
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimension of the domain.  
      """
      return self.__getdomainn_L_2(*args,**kwds)
    def __getpowerdomaininfo_L_2(self,domidx):
      _res_getpowerdomaininfo,_retargs_getpowerdomaininfo = self.__obj.getpowerdomaininfo_L_2(domidx)
      if _res_getpowerdomaininfo != 0:
        _,_msg_getpowerdomaininfo = self.__getlasterror(_res_getpowerdomaininfo)
        raise Error(rescode(_res_getpowerdomaininfo),_msg_getpowerdomaininfo)
      else:
        (n,nleft) = _retargs_getpowerdomaininfo
      return (n,nleft)
    def getpowerdomaininfo(self,*args,**kwds):
      """
      Obtains structural information about a power domain.
    
      getpowerdomaininfo(domidx) -> (n,nleft)
        [domidx : int64]  Index of the domain.  
        [n : int64]  Dimension of the domain.  
        [nleft : int64]  Number of variables on the left hand side.  
      """
      return self.__getpowerdomaininfo_L_2(*args,**kwds)
    def __getpowerdomainalpha_LO_3(self,domidx,alpha):
      if alpha is None:
        raise TypeError("Argument alpha may not be None")
      copyback_alpha = False
      if alpha is None:
        alpha_ = None
        memview_alpha = None
      else:
        try:
          memview_alpha = memoryview(alpha)
        except TypeError:
          try:
            _tmparray_alpha = array.array("d",[0 for _ in range(len(alpha))])
          except TypeError:
            raise TypeError("Argument alpha has wrong type") from None
          else:
            memview_alpha = memoryview(_tmparray_alpha)
            copyback_alpha = True
            alpha_ = _tmparray_alpha
        else:
          if memview_alpha.ndim != 1:
            raise TypeError("Argument alpha must be one-dimensional")
          if memview_alpha.format != "d":
            _tmparray_alpha = array.array("d",alpha)
            memview_alpha = memoryview(_tmparray_alpha)
            copyback_alpha = True
            alpha_ = _tmparray_alpha
      _res_getpowerdomainalpha,_retargs_getpowerdomainalpha = self.__obj.getpowerdomainalpha_LO_3(domidx,memview_alpha)
      if _res_getpowerdomainalpha != 0:
        _,_msg_getpowerdomainalpha = self.__getlasterror(_res_getpowerdomainalpha)
        raise Error(rescode(_res_getpowerdomainalpha),_msg_getpowerdomainalpha)
      if copyback_alpha:
        for __tmp_1373 in range(len(alpha)): alpha[__tmp_1373] = alpha_[__tmp_1373]
    def __getpowerdomainalpha_LO_2(self,domidx):
      alpha_ = bytearray(0)
      _res_getpowerdomainalpha,_retargs_getpowerdomainalpha = self.__obj.getpowerdomainalpha_LO_2(domidx,alpha_)
      if _res_getpowerdomainalpha != 0:
        _,_msg_getpowerdomainalpha = self.__getlasterror(_res_getpowerdomainalpha)
        raise Error(rescode(_res_getpowerdomainalpha),_msg_getpowerdomainalpha)
      alpha = array.array("d")
      alpha.frombytes(alpha_)
      return (alpha)
    def getpowerdomainalpha(self,*args,**kwds):
      """
      Obtains the exponent vector of a power domain.
    
      getpowerdomainalpha(domidx,alpha)
      getpowerdomainalpha(domidx) -> (alpha)
        [alpha : array(float64)]  The exponent vector of the domain.  
        [domidx : int64]  Index of the domain.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 3: return self.__getpowerdomainalpha_LO_3(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getpowerdomainalpha_LO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __appendsparsesymmat_iOOO_5(self,dim,subi,subj,valij):
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",subi)
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if valij is None:
        raise TypeError("Argument valij may not be None")
      copyback_valij = False
      if valij is None:
        valij_ = None
        memview_valij = None
      else:
        try:
          memview_valij = memoryview(valij)
        except TypeError:
          try:
            _tmparray_valij = array.array("d",valij)
          except TypeError:
            raise TypeError("Argument valij has wrong type") from None
          else:
            memview_valij = memoryview(_tmparray_valij)
            copyback_valij = True
            valij_ = _tmparray_valij
        else:
          if memview_valij.ndim != 1:
            raise TypeError("Argument valij must be one-dimensional")
          if memview_valij.format != "d":
            _tmparray_valij = array.array("d",valij)
            memview_valij = memoryview(_tmparray_valij)
            copyback_valij = True
            valij_ = _tmparray_valij
      _res_appendsparsesymmat,_retargs_appendsparsesymmat = self.__obj.appendsparsesymmat_iOOO_5(dim,memview_subi,memview_subj,memview_valij)
      if _res_appendsparsesymmat != 0:
        _,_msg_appendsparsesymmat = self.__getlasterror(_res_appendsparsesymmat)
        raise Error(rescode(_res_appendsparsesymmat),_msg_appendsparsesymmat)
      else:
        (idx) = _retargs_appendsparsesymmat
      return (idx)
    def appendsparsesymmat(self,*args,**kwds):
      """
      Appends a general sparse symmetric matrix to the storage of symmetric matrices.
    
      appendsparsesymmat(dim,subi,subj,valij) -> (idx)
        [dim : int32]  Dimension of the symmetric matrix that is appended.  
        [idx : int64]  Unique index assigned to the inputted matrix.  
        [subi : array(int32)]  Row subscript in the triplets.  
        [subj : array(int32)]  Column subscripts in the triplets.  
        [valij : array(float64)]  Values of each triplet.  
      """
      return self.__appendsparsesymmat_iOOO_5(*args,**kwds)
    def __appendsparsesymmatlist_OOOOOO_7(self,dims,nz,subi,subj,valij,idx):
      if dims is None:
        raise TypeError("Argument dims may not be None")
      copyback_dims = False
      if dims is None:
        dims_ = None
        memview_dims = None
      else:
        try:
          memview_dims = memoryview(dims)
        except TypeError:
          try:
            _tmparray_dims = array.array("i",dims)
          except TypeError:
            raise TypeError("Argument dims has wrong type") from None
          else:
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
        else:
          if memview_dims.ndim != 1:
            raise TypeError("Argument dims must be one-dimensional")
          if memview_dims.format != "i":
            _tmparray_dims = array.array("i",dims)
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
      if nz is None:
        raise TypeError("Argument nz may not be None")
      copyback_nz = False
      if nz is None:
        nz_ = None
        memview_nz = None
      else:
        try:
          memview_nz = memoryview(nz)
        except TypeError:
          try:
            _tmparray_nz = array.array("q",nz)
          except TypeError:
            raise TypeError("Argument nz has wrong type") from None
          else:
            memview_nz = memoryview(_tmparray_nz)
            copyback_nz = True
            nz_ = _tmparray_nz
        else:
          if memview_nz.ndim != 1:
            raise TypeError("Argument nz must be one-dimensional")
          if memview_nz.format != "q":
            _tmparray_nz = array.array("q",nz)
            memview_nz = memoryview(_tmparray_nz)
            copyback_nz = True
            nz_ = _tmparray_nz
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",subi)
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if valij is None:
        raise TypeError("Argument valij may not be None")
      copyback_valij = False
      if valij is None:
        valij_ = None
        memview_valij = None
      else:
        try:
          memview_valij = memoryview(valij)
        except TypeError:
          try:
            _tmparray_valij = array.array("d",valij)
          except TypeError:
            raise TypeError("Argument valij has wrong type") from None
          else:
            memview_valij = memoryview(_tmparray_valij)
            copyback_valij = True
            valij_ = _tmparray_valij
        else:
          if memview_valij.ndim != 1:
            raise TypeError("Argument valij must be one-dimensional")
          if memview_valij.format != "d":
            _tmparray_valij = array.array("d",valij)
            memview_valij = memoryview(_tmparray_valij)
            copyback_valij = True
            valij_ = _tmparray_valij
      if idx is None:
        raise TypeError("Argument idx may not be None")
      copyback_idx = False
      if idx is None:
        idx_ = None
        memview_idx = None
      else:
        try:
          memview_idx = memoryview(idx)
        except TypeError:
          try:
            _tmparray_idx = array.array("q",[0 for _ in range(len(idx))])
          except TypeError:
            raise TypeError("Argument idx has wrong type") from None
          else:
            memview_idx = memoryview(_tmparray_idx)
            copyback_idx = True
            idx_ = _tmparray_idx
        else:
          if memview_idx.ndim != 1:
            raise TypeError("Argument idx must be one-dimensional")
          if memview_idx.format != "q":
            _tmparray_idx = array.array("q",idx)
            memview_idx = memoryview(_tmparray_idx)
            copyback_idx = True
            idx_ = _tmparray_idx
      _res_appendsparsesymmatlist,_retargs_appendsparsesymmatlist = self.__obj.appendsparsesymmatlist_OOOOOO_7(memview_dims,memview_nz,memview_subi,memview_subj,memview_valij,memview_idx)
      if _res_appendsparsesymmatlist != 0:
        _,_msg_appendsparsesymmatlist = self.__getlasterror(_res_appendsparsesymmatlist)
        raise Error(rescode(_res_appendsparsesymmatlist),_msg_appendsparsesymmatlist)
      if copyback_idx:
        for __tmp_1401 in range(len(idx)): idx[__tmp_1401] = idx_[__tmp_1401]
    def __appendsparsesymmatlist_OOOOOO_6(self,dims,nz,subi,subj,valij):
      if dims is None:
        raise TypeError("Argument dims may not be None")
      copyback_dims = False
      if dims is None:
        dims_ = None
        memview_dims = None
      else:
        try:
          memview_dims = memoryview(dims)
        except TypeError:
          try:
            _tmparray_dims = array.array("i",dims)
          except TypeError:
            raise TypeError("Argument dims has wrong type") from None
          else:
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
        else:
          if memview_dims.ndim != 1:
            raise TypeError("Argument dims must be one-dimensional")
          if memview_dims.format != "i":
            _tmparray_dims = array.array("i",dims)
            memview_dims = memoryview(_tmparray_dims)
            copyback_dims = True
            dims_ = _tmparray_dims
      if nz is None:
        raise TypeError("Argument nz may not be None")
      copyback_nz = False
      if nz is None:
        nz_ = None
        memview_nz = None
      else:
        try:
          memview_nz = memoryview(nz)
        except TypeError:
          try:
            _tmparray_nz = array.array("q",nz)
          except TypeError:
            raise TypeError("Argument nz has wrong type") from None
          else:
            memview_nz = memoryview(_tmparray_nz)
            copyback_nz = True
            nz_ = _tmparray_nz
        else:
          if memview_nz.ndim != 1:
            raise TypeError("Argument nz must be one-dimensional")
          if memview_nz.format != "q":
            _tmparray_nz = array.array("q",nz)
            memview_nz = memoryview(_tmparray_nz)
            copyback_nz = True
            nz_ = _tmparray_nz
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",subi)
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if valij is None:
        raise TypeError("Argument valij may not be None")
      copyback_valij = False
      if valij is None:
        valij_ = None
        memview_valij = None
      else:
        try:
          memview_valij = memoryview(valij)
        except TypeError:
          try:
            _tmparray_valij = array.array("d",valij)
          except TypeError:
            raise TypeError("Argument valij has wrong type") from None
          else:
            memview_valij = memoryview(_tmparray_valij)
            copyback_valij = True
            valij_ = _tmparray_valij
        else:
          if memview_valij.ndim != 1:
            raise TypeError("Argument valij must be one-dimensional")
          if memview_valij.format != "d":
            _tmparray_valij = array.array("d",valij)
            memview_valij = memoryview(_tmparray_valij)
            copyback_valij = True
            valij_ = _tmparray_valij
      idx_ = bytearray(0)
      _res_appendsparsesymmatlist,_retargs_appendsparsesymmatlist = self.__obj.appendsparsesymmatlist_OOOOOO_6(memview_dims,memview_nz,memview_subi,memview_subj,memview_valij,idx_)
      if _res_appendsparsesymmatlist != 0:
        _,_msg_appendsparsesymmatlist = self.__getlasterror(_res_appendsparsesymmatlist)
        raise Error(rescode(_res_appendsparsesymmatlist),_msg_appendsparsesymmatlist)
      idx = array.array("q")
      idx.frombytes(idx_)
      return (idx)
    def appendsparsesymmatlist(self,*args,**kwds):
      """
      Appends a general sparse symmetric matrix to the storage of symmetric matrices.
    
      appendsparsesymmatlist(dims,nz,subi,subj,valij,idx)
      appendsparsesymmatlist(dims,nz,subi,subj,valij) -> (idx)
        [dims : array(int32)]  Dimensions of the symmetric matrixes.  
        [idx : array(int64)]  Unique index assigned to the inputted matrix.  
        [nz : array(int64)]  Number of nonzeros for each matrix.  
        [subi : array(int32)]  Row subscript in the triplets.  
        [subj : array(int32)]  Column subscripts in the triplets.  
        [valij : array(float64)]  Values of each triplet.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 7: return self.__appendsparsesymmatlist_OOOOOO_7(*args,**kwds)
      elif len(args)+len(kwds)+1 == 6: return self.__appendsparsesymmatlist_OOOOOO_6(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __getsymmatinfo_L_2(self,idx):
      _res_getsymmatinfo,_retargs_getsymmatinfo = self.__obj.getsymmatinfo_L_2(idx)
      if _res_getsymmatinfo != 0:
        _,_msg_getsymmatinfo = self.__getlasterror(_res_getsymmatinfo)
        raise Error(rescode(_res_getsymmatinfo),_msg_getsymmatinfo)
      else:
        (dim,nz,mattype) = _retargs_getsymmatinfo
      return (dim,nz,symmattype(mattype))
    def getsymmatinfo(self,*args,**kwds):
      """
      Obtains information about a matrix from the symmetric matrix storage.
    
      getsymmatinfo(idx) -> (dim,nz,mattype)
        [dim : int32]  Returns the dimension of the requested matrix.  
        [idx : int64]  Index of the matrix for which information is requested.  
        [mattype : mosek.symmattype]  Returns the type of the requested matrix.  
        [nz : int64]  Returns the number of non-zeros in the requested matrix.  
      """
      return self.__getsymmatinfo_L_2(*args,**kwds)
    def __getnumsymmat__1(self):
      _res_getnumsymmat,_retargs_getnumsymmat = self.__obj.getnumsymmat__1()
      if _res_getnumsymmat != 0:
        _,_msg_getnumsymmat = self.__getlasterror(_res_getnumsymmat)
        raise Error(rescode(_res_getnumsymmat),_msg_getnumsymmat)
      else:
        (num) = _retargs_getnumsymmat
      return (num)
    def getnumsymmat(self,*args,**kwds):
      """
      Obtains the number of symmetric matrices stored.
    
      getnumsymmat() -> (num)
        [num : int64]  The number of symmetric sparse matrices.  
      """
      return self.__getnumsymmat__1(*args,**kwds)
    def __getsparsesymmat_LOOO_5(self,idx,subi,subj,valij):
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",[0 for _ in range(len(subi))])
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",[0 for _ in range(len(subj))])
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      copyback_valij = False
      if valij is None:
        valij_ = None
        memview_valij = None
      else:
        try:
          memview_valij = memoryview(valij)
        except TypeError:
          try:
            _tmparray_valij = array.array("d",[0 for _ in range(len(valij))])
          except TypeError:
            raise TypeError("Argument valij has wrong type") from None
          else:
            memview_valij = memoryview(_tmparray_valij)
            copyback_valij = True
            valij_ = _tmparray_valij
        else:
          if memview_valij.ndim != 1:
            raise TypeError("Argument valij must be one-dimensional")
          if memview_valij.format != "d":
            _tmparray_valij = array.array("d",valij)
            memview_valij = memoryview(_tmparray_valij)
            copyback_valij = True
            valij_ = _tmparray_valij
      _res_getsparsesymmat,_retargs_getsparsesymmat = self.__obj.getsparsesymmat_LOOO_5(idx,memview_subi,memview_subj,memview_valij)
      if _res_getsparsesymmat != 0:
        _,_msg_getsparsesymmat = self.__getlasterror(_res_getsparsesymmat)
        raise Error(rescode(_res_getsparsesymmat),_msg_getsparsesymmat)
      if copyback_subi:
        for __tmp_1424 in range(len(subi)): subi[__tmp_1424] = subi_[__tmp_1424]
      if copyback_subj:
        for __tmp_1425 in range(len(subj)): subj[__tmp_1425] = subj_[__tmp_1425]
      if copyback_valij:
        for __tmp_1426 in range(len(valij)): valij[__tmp_1426] = valij_[__tmp_1426]
    def __getsparsesymmat_LOOO_2(self,idx):
      subi_ = bytearray(0)
      subj_ = bytearray(0)
      valij_ = bytearray(0)
      _res_getsparsesymmat,_retargs_getsparsesymmat = self.__obj.getsparsesymmat_LOOO_2(idx,subi_,subj_,valij_)
      if _res_getsparsesymmat != 0:
        _,_msg_getsparsesymmat = self.__getlasterror(_res_getsparsesymmat)
        raise Error(rescode(_res_getsparsesymmat),_msg_getsparsesymmat)
      subi = array.array("i")
      subi.frombytes(subi_)
      subj = array.array("i")
      subj.frombytes(subj_)
      valij = array.array("d")
      valij.frombytes(valij_)
      return (subi,subj,valij)
    def getsparsesymmat(self,*args,**kwds):
      """
      Gets a single symmetric matrix from the matrix store.
    
      getsparsesymmat(idx,subi,subj,valij)
      getsparsesymmat(idx) -> (subi,subj,valij)
        [idx : int64]  Index of the matrix to retrieve.  
        [subi : array(int32)]  Row subscripts of the matrix non-zero elements.  
        [subj : array(int32)]  Column subscripts of the matrix non-zero elements.  
        [valij : array(float64)]  Coefficients of the matrix non-zero elements.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 5: return self.__getsparsesymmat_LOOO_5(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__getsparsesymmat_LOOO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __putdouparam_id_3(self,param,parvalue):
      _res_putdouparam,_retargs_putdouparam = self.__obj.putdouparam_id_3(param,parvalue)
      if _res_putdouparam != 0:
        _,_msg_putdouparam = self.__getlasterror(_res_putdouparam)
        raise Error(rescode(_res_putdouparam),_msg_putdouparam)
    def putdouparam(self,*args,**kwds):
      """
      Sets a double parameter.
    
      putdouparam(param,parvalue)
        [param : mosek.dparam]  Which parameter.  
        [parvalue : float64]  Parameter value.  
      """
      return self.__putdouparam_id_3(*args,**kwds)
    def __putintparam_ii_3(self,param,parvalue):
      _res_putintparam,_retargs_putintparam = self.__obj.putintparam_ii_3(param,parvalue)
      if _res_putintparam != 0:
        _,_msg_putintparam = self.__getlasterror(_res_putintparam)
        raise Error(rescode(_res_putintparam),_msg_putintparam)
    def putintparam(self,*args,**kwds):
      """
      Sets an integer parameter.
    
      putintparam(param,parvalue)
        [param : mosek.iparam]  Which parameter.  
        [parvalue : int32]  Parameter value.  
      """
      return self.__putintparam_ii_3(*args,**kwds)
    def __putmaxnumcon_i_2(self,maxnumcon):
      _res_putmaxnumcon,_retargs_putmaxnumcon = self.__obj.putmaxnumcon_i_2(maxnumcon)
      if _res_putmaxnumcon != 0:
        _,_msg_putmaxnumcon = self.__getlasterror(_res_putmaxnumcon)
        raise Error(rescode(_res_putmaxnumcon),_msg_putmaxnumcon)
    def putmaxnumcon(self,*args,**kwds):
      """
      Sets the number of preallocated constraints in the optimization task.
    
      putmaxnumcon(maxnumcon)
        [maxnumcon : int32]  Number of preallocated constraints in the optimization task.  
      """
      return self.__putmaxnumcon_i_2(*args,**kwds)
    def __putmaxnumcone_i_2(self,maxnumcone):
      _res_putmaxnumcone,_retargs_putmaxnumcone = self.__obj.putmaxnumcone_i_2(maxnumcone)
      if _res_putmaxnumcone != 0:
        _,_msg_putmaxnumcone = self.__getlasterror(_res_putmaxnumcone)
        raise Error(rescode(_res_putmaxnumcone),_msg_putmaxnumcone)
    def putmaxnumcone(self,*args,**kwds):
      """
      Sets the number of preallocated conic constraints in the optimization task.
    
      putmaxnumcone(maxnumcone)
        [maxnumcone : int32]  Number of preallocated conic constraints in the optimization task.  
      """
      return self.__putmaxnumcone_i_2(*args,**kwds)
    def __getmaxnumcone__1(self):
      _res_getmaxnumcone,_retargs_getmaxnumcone = self.__obj.getmaxnumcone__1()
      if _res_getmaxnumcone != 0:
        _,_msg_getmaxnumcone = self.__getlasterror(_res_getmaxnumcone)
        raise Error(rescode(_res_getmaxnumcone),_msg_getmaxnumcone)
      else:
        (maxnumcone) = _retargs_getmaxnumcone
      return (maxnumcone)
    def getmaxnumcone(self,*args,**kwds):
      """
      Obtains the number of preallocated cones in the optimization task.
    
      getmaxnumcone() -> (maxnumcone)
        [maxnumcone : int32]  Number of preallocated conic constraints in the optimization task.  
      """
      return self.__getmaxnumcone__1(*args,**kwds)
    def __putmaxnumvar_i_2(self,maxnumvar):
      _res_putmaxnumvar,_retargs_putmaxnumvar = self.__obj.putmaxnumvar_i_2(maxnumvar)
      if _res_putmaxnumvar != 0:
        _,_msg_putmaxnumvar = self.__getlasterror(_res_putmaxnumvar)
        raise Error(rescode(_res_putmaxnumvar),_msg_putmaxnumvar)
    def putmaxnumvar(self,*args,**kwds):
      """
      Sets the number of preallocated variables in the optimization task.
    
      putmaxnumvar(maxnumvar)
        [maxnumvar : int32]  Number of preallocated variables in the optimization task.  
      """
      return self.__putmaxnumvar_i_2(*args,**kwds)
    def __putmaxnumbarvar_i_2(self,maxnumbarvar):
      _res_putmaxnumbarvar,_retargs_putmaxnumbarvar = self.__obj.putmaxnumbarvar_i_2(maxnumbarvar)
      if _res_putmaxnumbarvar != 0:
        _,_msg_putmaxnumbarvar = self.__getlasterror(_res_putmaxnumbarvar)
        raise Error(rescode(_res_putmaxnumbarvar),_msg_putmaxnumbarvar)
    def putmaxnumbarvar(self,*args,**kwds):
      """
      Sets the number of preallocated symmetric matrix variables.
    
      putmaxnumbarvar(maxnumbarvar)
        [maxnumbarvar : int32]  Number of preallocated symmetric matrix variables.  
      """
      return self.__putmaxnumbarvar_i_2(*args,**kwds)
    def __putmaxnumanz_L_2(self,maxnumanz):
      _res_putmaxnumanz,_retargs_putmaxnumanz = self.__obj.putmaxnumanz_L_2(maxnumanz)
      if _res_putmaxnumanz != 0:
        _,_msg_putmaxnumanz = self.__getlasterror(_res_putmaxnumanz)
        raise Error(rescode(_res_putmaxnumanz),_msg_putmaxnumanz)
    def putmaxnumanz(self,*args,**kwds):
      """
      Sets the number of preallocated non-zero entries in the linear coefficient matrix.
    
      putmaxnumanz(maxnumanz)
        [maxnumanz : int64]  New size of the storage reserved for storing the linear coefficient matrix.  
      """
      return self.__putmaxnumanz_L_2(*args,**kwds)
    def __putmaxnumqnz_L_2(self,maxnumqnz):
      _res_putmaxnumqnz,_retargs_putmaxnumqnz = self.__obj.putmaxnumqnz_L_2(maxnumqnz)
      if _res_putmaxnumqnz != 0:
        _,_msg_putmaxnumqnz = self.__getlasterror(_res_putmaxnumqnz)
        raise Error(rescode(_res_putmaxnumqnz),_msg_putmaxnumqnz)
    def putmaxnumqnz(self,*args,**kwds):
      """
      Sets the number of preallocated non-zero entries in quadratic terms.
    
      putmaxnumqnz(maxnumqnz)
        [maxnumqnz : int64]  Number of non-zero elements preallocated in quadratic coefficient matrices.  
      """
      return self.__putmaxnumqnz_L_2(*args,**kwds)
    def __getmaxnumqnz64__1(self):
      _res_getmaxnumqnz64,_retargs_getmaxnumqnz64 = self.__obj.getmaxnumqnz64__1()
      if _res_getmaxnumqnz64 != 0:
        _,_msg_getmaxnumqnz64 = self.__getlasterror(_res_getmaxnumqnz64)
        raise Error(rescode(_res_getmaxnumqnz64),_msg_getmaxnumqnz64)
      else:
        (maxnumqnz) = _retargs_getmaxnumqnz64
      return (maxnumqnz)
    def getmaxnumqnz(self,*args,**kwds):
      """
      Obtains the number of preallocated non-zeros for all quadratic terms in objective and constraints.
    
      getmaxnumqnz() -> (maxnumqnz)
        [maxnumqnz : int64]  Number of non-zero elements preallocated in quadratic coefficient matrices.  
      """
      return self.__getmaxnumqnz64__1(*args,**kwds)
    def __putnadouparam_sd_3(self,paramname,parvalue):
      _res_putnadouparam,_retargs_putnadouparam = self.__obj.putnadouparam_sd_3(paramname,parvalue)
      if _res_putnadouparam != 0:
        _,_msg_putnadouparam = self.__getlasterror(_res_putnadouparam)
        raise Error(rescode(_res_putnadouparam),_msg_putnadouparam)
    def putnadouparam(self,*args,**kwds):
      """
      Sets a double parameter.
    
      putnadouparam(paramname,parvalue)
        [paramname : str]  Name of a parameter.  
        [parvalue : float64]  Parameter value.  
      """
      return self.__putnadouparam_sd_3(*args,**kwds)
    def __putnaintparam_si_3(self,paramname,parvalue):
      _res_putnaintparam,_retargs_putnaintparam = self.__obj.putnaintparam_si_3(paramname,parvalue)
      if _res_putnaintparam != 0:
        _,_msg_putnaintparam = self.__getlasterror(_res_putnaintparam)
        raise Error(rescode(_res_putnaintparam),_msg_putnaintparam)
    def putnaintparam(self,*args,**kwds):
      """
      Sets an integer parameter.
    
      putnaintparam(paramname,parvalue)
        [paramname : str]  Name of a parameter.  
        [parvalue : int32]  Parameter value.  
      """
      return self.__putnaintparam_si_3(*args,**kwds)
    def __putnastrparam_ss_3(self,paramname,parvalue):
      _res_putnastrparam,_retargs_putnastrparam = self.__obj.putnastrparam_ss_3(paramname,parvalue)
      if _res_putnastrparam != 0:
        _,_msg_putnastrparam = self.__getlasterror(_res_putnastrparam)
        raise Error(rescode(_res_putnastrparam),_msg_putnastrparam)
    def putnastrparam(self,*args,**kwds):
      """
      Sets a string parameter.
    
      putnastrparam(paramname,parvalue)
        [paramname : str]  Name of a parameter.  
        [parvalue : str]  Parameter value.  
      """
      return self.__putnastrparam_ss_3(*args,**kwds)
    def __putobjname_s_2(self,objname):
      _res_putobjname,_retargs_putobjname = self.__obj.putobjname_s_2(objname)
      if _res_putobjname != 0:
        _,_msg_putobjname = self.__getlasterror(_res_putobjname)
        raise Error(rescode(_res_putobjname),_msg_putobjname)
    def putobjname(self,*args,**kwds):
      """
      Assigns a new name to the objective.
    
      putobjname(objname)
        [objname : str]  Name of the objective.  
      """
      return self.__putobjname_s_2(*args,**kwds)
    def __putparam_ss_3(self,parname,parvalue):
      _res_putparam,_retargs_putparam = self.__obj.putparam_ss_3(parname,parvalue)
      if _res_putparam != 0:
        _,_msg_putparam = self.__getlasterror(_res_putparam)
        raise Error(rescode(_res_putparam),_msg_putparam)
    def putparam(self,*args,**kwds):
      """
      Modifies the value of parameter.
    
      putparam(parname,parvalue)
        [parname : str]  Parameter name.  
        [parvalue : str]  Parameter value.  
      """
      return self.__putparam_ss_3(*args,**kwds)
    def __putqcon_OOOO_5(self,qcsubk,qcsubi,qcsubj,qcval):
      if qcsubk is None:
        raise TypeError("Argument qcsubk may not be None")
      copyback_qcsubk = False
      if qcsubk is None:
        qcsubk_ = None
        memview_qcsubk = None
      else:
        try:
          memview_qcsubk = memoryview(qcsubk)
        except TypeError:
          try:
            _tmparray_qcsubk = array.array("i",qcsubk)
          except TypeError:
            raise TypeError("Argument qcsubk has wrong type") from None
          else:
            memview_qcsubk = memoryview(_tmparray_qcsubk)
            copyback_qcsubk = True
            qcsubk_ = _tmparray_qcsubk
        else:
          if memview_qcsubk.ndim != 1:
            raise TypeError("Argument qcsubk must be one-dimensional")
          if memview_qcsubk.format != "i":
            _tmparray_qcsubk = array.array("i",qcsubk)
            memview_qcsubk = memoryview(_tmparray_qcsubk)
            copyback_qcsubk = True
            qcsubk_ = _tmparray_qcsubk
      if qcsubi is None:
        raise TypeError("Argument qcsubi may not be None")
      copyback_qcsubi = False
      if qcsubi is None:
        qcsubi_ = None
        memview_qcsubi = None
      else:
        try:
          memview_qcsubi = memoryview(qcsubi)
        except TypeError:
          try:
            _tmparray_qcsubi = array.array("i",qcsubi)
          except TypeError:
            raise TypeError("Argument qcsubi has wrong type") from None
          else:
            memview_qcsubi = memoryview(_tmparray_qcsubi)
            copyback_qcsubi = True
            qcsubi_ = _tmparray_qcsubi
        else:
          if memview_qcsubi.ndim != 1:
            raise TypeError("Argument qcsubi must be one-dimensional")
          if memview_qcsubi.format != "i":
            _tmparray_qcsubi = array.array("i",qcsubi)
            memview_qcsubi = memoryview(_tmparray_qcsubi)
            copyback_qcsubi = True
            qcsubi_ = _tmparray_qcsubi
      if qcsubj is None:
        raise TypeError("Argument qcsubj may not be None")
      copyback_qcsubj = False
      if qcsubj is None:
        qcsubj_ = None
        memview_qcsubj = None
      else:
        try:
          memview_qcsubj = memoryview(qcsubj)
        except TypeError:
          try:
            _tmparray_qcsubj = array.array("i",qcsubj)
          except TypeError:
            raise TypeError("Argument qcsubj has wrong type") from None
          else:
            memview_qcsubj = memoryview(_tmparray_qcsubj)
            copyback_qcsubj = True
            qcsubj_ = _tmparray_qcsubj
        else:
          if memview_qcsubj.ndim != 1:
            raise TypeError("Argument qcsubj must be one-dimensional")
          if memview_qcsubj.format != "i":
            _tmparray_qcsubj = array.array("i",qcsubj)
            memview_qcsubj = memoryview(_tmparray_qcsubj)
            copyback_qcsubj = True
            qcsubj_ = _tmparray_qcsubj
      if qcval is None:
        raise TypeError("Argument qcval may not be None")
      copyback_qcval = False
      if qcval is None:
        qcval_ = None
        memview_qcval = None
      else:
        try:
          memview_qcval = memoryview(qcval)
        except TypeError:
          try:
            _tmparray_qcval = array.array("d",qcval)
          except TypeError:
            raise TypeError("Argument qcval has wrong type") from None
          else:
            memview_qcval = memoryview(_tmparray_qcval)
            copyback_qcval = True
            qcval_ = _tmparray_qcval
        else:
          if memview_qcval.ndim != 1:
            raise TypeError("Argument qcval must be one-dimensional")
          if memview_qcval.format != "d":
            _tmparray_qcval = array.array("d",qcval)
            memview_qcval = memoryview(_tmparray_qcval)
            copyback_qcval = True
            qcval_ = _tmparray_qcval
      _res_putqcon,_retargs_putqcon = self.__obj.putqcon_OOOO_5(memview_qcsubk,memview_qcsubi,memview_qcsubj,memview_qcval)
      if _res_putqcon != 0:
        _,_msg_putqcon = self.__getlasterror(_res_putqcon)
        raise Error(rescode(_res_putqcon),_msg_putqcon)
    def putqcon(self,*args,**kwds):
      """
      Replaces all quadratic terms in constraints.
    
      putqcon(qcsubk,qcsubi,qcsubj,qcval)
        [qcsubi : array(int32)]  Row subscripts for quadratic constraint matrix.  
        [qcsubj : array(int32)]  Column subscripts for quadratic constraint matrix.  
        [qcsubk : array(int32)]  Constraint subscripts for quadratic coefficients.  
        [qcval : array(float64)]  Quadratic constraint coefficient values.  
      """
      return self.__putqcon_OOOO_5(*args,**kwds)
    def __putqconk_iOOO_5(self,k,qcsubi,qcsubj,qcval):
      if qcsubi is None:
        raise TypeError("Argument qcsubi may not be None")
      copyback_qcsubi = False
      if qcsubi is None:
        qcsubi_ = None
        memview_qcsubi = None
      else:
        try:
          memview_qcsubi = memoryview(qcsubi)
        except TypeError:
          try:
            _tmparray_qcsubi = array.array("i",qcsubi)
          except TypeError:
            raise TypeError("Argument qcsubi has wrong type") from None
          else:
            memview_qcsubi = memoryview(_tmparray_qcsubi)
            copyback_qcsubi = True
            qcsubi_ = _tmparray_qcsubi
        else:
          if memview_qcsubi.ndim != 1:
            raise TypeError("Argument qcsubi must be one-dimensional")
          if memview_qcsubi.format != "i":
            _tmparray_qcsubi = array.array("i",qcsubi)
            memview_qcsubi = memoryview(_tmparray_qcsubi)
            copyback_qcsubi = True
            qcsubi_ = _tmparray_qcsubi
      if qcsubj is None:
        raise TypeError("Argument qcsubj may not be None")
      copyback_qcsubj = False
      if qcsubj is None:
        qcsubj_ = None
        memview_qcsubj = None
      else:
        try:
          memview_qcsubj = memoryview(qcsubj)
        except TypeError:
          try:
            _tmparray_qcsubj = array.array("i",qcsubj)
          except TypeError:
            raise TypeError("Argument qcsubj has wrong type") from None
          else:
            memview_qcsubj = memoryview(_tmparray_qcsubj)
            copyback_qcsubj = True
            qcsubj_ = _tmparray_qcsubj
        else:
          if memview_qcsubj.ndim != 1:
            raise TypeError("Argument qcsubj must be one-dimensional")
          if memview_qcsubj.format != "i":
            _tmparray_qcsubj = array.array("i",qcsubj)
            memview_qcsubj = memoryview(_tmparray_qcsubj)
            copyback_qcsubj = True
            qcsubj_ = _tmparray_qcsubj
      if qcval is None:
        raise TypeError("Argument qcval may not be None")
      copyback_qcval = False
      if qcval is None:
        qcval_ = None
        memview_qcval = None
      else:
        try:
          memview_qcval = memoryview(qcval)
        except TypeError:
          try:
            _tmparray_qcval = array.array("d",qcval)
          except TypeError:
            raise TypeError("Argument qcval has wrong type") from None
          else:
            memview_qcval = memoryview(_tmparray_qcval)
            copyback_qcval = True
            qcval_ = _tmparray_qcval
        else:
          if memview_qcval.ndim != 1:
            raise TypeError("Argument qcval must be one-dimensional")
          if memview_qcval.format != "d":
            _tmparray_qcval = array.array("d",qcval)
            memview_qcval = memoryview(_tmparray_qcval)
            copyback_qcval = True
            qcval_ = _tmparray_qcval
      _res_putqconk,_retargs_putqconk = self.__obj.putqconk_iOOO_5(k,memview_qcsubi,memview_qcsubj,memview_qcval)
      if _res_putqconk != 0:
        _,_msg_putqconk = self.__getlasterror(_res_putqconk)
        raise Error(rescode(_res_putqconk),_msg_putqconk)
    def putqconk(self,*args,**kwds):
      """
      Replaces all quadratic terms in a single constraint.
    
      putqconk(k,qcsubi,qcsubj,qcval)
        [k : int32]  The constraint in which the new quadratic elements are inserted.  
        [qcsubi : array(int32)]  Row subscripts for quadratic constraint matrix.  
        [qcsubj : array(int32)]  Column subscripts for quadratic constraint matrix.  
        [qcval : array(float64)]  Quadratic constraint coefficient values.  
      """
      return self.__putqconk_iOOO_5(*args,**kwds)
    def __putqobj_OOO_4(self,qosubi,qosubj,qoval):
      if qosubi is None:
        raise TypeError("Argument qosubi may not be None")
      copyback_qosubi = False
      if qosubi is None:
        qosubi_ = None
        memview_qosubi = None
      else:
        try:
          memview_qosubi = memoryview(qosubi)
        except TypeError:
          try:
            _tmparray_qosubi = array.array("i",qosubi)
          except TypeError:
            raise TypeError("Argument qosubi has wrong type") from None
          else:
            memview_qosubi = memoryview(_tmparray_qosubi)
            copyback_qosubi = True
            qosubi_ = _tmparray_qosubi
        else:
          if memview_qosubi.ndim != 1:
            raise TypeError("Argument qosubi must be one-dimensional")
          if memview_qosubi.format != "i":
            _tmparray_qosubi = array.array("i",qosubi)
            memview_qosubi = memoryview(_tmparray_qosubi)
            copyback_qosubi = True
            qosubi_ = _tmparray_qosubi
      if qosubj is None:
        raise TypeError("Argument qosubj may not be None")
      copyback_qosubj = False
      if qosubj is None:
        qosubj_ = None
        memview_qosubj = None
      else:
        try:
          memview_qosubj = memoryview(qosubj)
        except TypeError:
          try:
            _tmparray_qosubj = array.array("i",qosubj)
          except TypeError:
            raise TypeError("Argument qosubj has wrong type") from None
          else:
            memview_qosubj = memoryview(_tmparray_qosubj)
            copyback_qosubj = True
            qosubj_ = _tmparray_qosubj
        else:
          if memview_qosubj.ndim != 1:
            raise TypeError("Argument qosubj must be one-dimensional")
          if memview_qosubj.format != "i":
            _tmparray_qosubj = array.array("i",qosubj)
            memview_qosubj = memoryview(_tmparray_qosubj)
            copyback_qosubj = True
            qosubj_ = _tmparray_qosubj
      if qoval is None:
        raise TypeError("Argument qoval may not be None")
      copyback_qoval = False
      if qoval is None:
        qoval_ = None
        memview_qoval = None
      else:
        try:
          memview_qoval = memoryview(qoval)
        except TypeError:
          try:
            _tmparray_qoval = array.array("d",qoval)
          except TypeError:
            raise TypeError("Argument qoval has wrong type") from None
          else:
            memview_qoval = memoryview(_tmparray_qoval)
            copyback_qoval = True
            qoval_ = _tmparray_qoval
        else:
          if memview_qoval.ndim != 1:
            raise TypeError("Argument qoval must be one-dimensional")
          if memview_qoval.format != "d":
            _tmparray_qoval = array.array("d",qoval)
            memview_qoval = memoryview(_tmparray_qoval)
            copyback_qoval = True
            qoval_ = _tmparray_qoval
      _res_putqobj,_retargs_putqobj = self.__obj.putqobj_OOO_4(memview_qosubi,memview_qosubj,memview_qoval)
      if _res_putqobj != 0:
        _,_msg_putqobj = self.__getlasterror(_res_putqobj)
        raise Error(rescode(_res_putqobj),_msg_putqobj)
    def putqobj(self,*args,**kwds):
      """
      Replaces all quadratic terms in the objective.
    
      putqobj(qosubi,qosubj,qoval)
        [qosubi : array(int32)]  Row subscripts for quadratic objective coefficients.  
        [qosubj : array(int32)]  Column subscripts for quadratic objective coefficients.  
        [qoval : array(float64)]  Quadratic objective coefficient values.  
      """
      return self.__putqobj_OOO_4(*args,**kwds)
    def __putqobjij_iid_4(self,i,j,qoij):
      _res_putqobjij,_retargs_putqobjij = self.__obj.putqobjij_iid_4(i,j,qoij)
      if _res_putqobjij != 0:
        _,_msg_putqobjij = self.__getlasterror(_res_putqobjij)
        raise Error(rescode(_res_putqobjij),_msg_putqobjij)
    def putqobjij(self,*args,**kwds):
      """
      Replaces one coefficient in the quadratic term in the objective.
    
      putqobjij(i,j,qoij)
        [i : int32]  Row index for the coefficient to be replaced.  
        [j : int32]  Column index for the coefficient to be replaced.  
        [qoij : float64]  The new coefficient value.  
      """
      return self.__putqobjij_iid_4(*args,**kwds)
    def __putsolution_iOOOOOOOOOOO_13(self,whichsol,skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx):
      if skc is None:
        skc_ = None
      else:
        # i
        _tmparray_skc_ = array.array("i",skc)
        skc_ = memoryview(_tmparray_skc_)
      if skx is None:
        skx_ = None
      else:
        # i
        _tmparray_skx_ = array.array("i",skx)
        skx_ = memoryview(_tmparray_skx_)
      if skn is None:
        skn_ = None
      else:
        # i
        _tmparray_skn_ = array.array("i",skn)
        skn_ = memoryview(_tmparray_skn_)
      copyback_xc = False
      if xc is None:
        xc_ = None
        memview_xc = None
      else:
        try:
          memview_xc = memoryview(xc)
        except TypeError:
          try:
            _tmparray_xc = array.array("d",xc)
          except TypeError:
            raise TypeError("Argument xc has wrong type") from None
          else:
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
        else:
          if memview_xc.ndim != 1:
            raise TypeError("Argument xc must be one-dimensional")
          if memview_xc.format != "d":
            _tmparray_xc = array.array("d",xc)
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
      copyback_xx = False
      if xx is None:
        xx_ = None
        memview_xx = None
      else:
        try:
          memview_xx = memoryview(xx)
        except TypeError:
          try:
            _tmparray_xx = array.array("d",xx)
          except TypeError:
            raise TypeError("Argument xx has wrong type") from None
          else:
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
        else:
          if memview_xx.ndim != 1:
            raise TypeError("Argument xx must be one-dimensional")
          if memview_xx.format != "d":
            _tmparray_xx = array.array("d",xx)
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
      copyback_y = False
      if y is None:
        y_ = None
        memview_y = None
      else:
        try:
          memview_y = memoryview(y)
        except TypeError:
          try:
            _tmparray_y = array.array("d",y)
          except TypeError:
            raise TypeError("Argument y has wrong type") from None
          else:
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
        else:
          if memview_y.ndim != 1:
            raise TypeError("Argument y must be one-dimensional")
          if memview_y.format != "d":
            _tmparray_y = array.array("d",y)
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
      copyback_slc = False
      if slc is None:
        slc_ = None
        memview_slc = None
      else:
        try:
          memview_slc = memoryview(slc)
        except TypeError:
          try:
            _tmparray_slc = array.array("d",slc)
          except TypeError:
            raise TypeError("Argument slc has wrong type") from None
          else:
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
        else:
          if memview_slc.ndim != 1:
            raise TypeError("Argument slc must be one-dimensional")
          if memview_slc.format != "d":
            _tmparray_slc = array.array("d",slc)
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
      copyback_suc = False
      if suc is None:
        suc_ = None
        memview_suc = None
      else:
        try:
          memview_suc = memoryview(suc)
        except TypeError:
          try:
            _tmparray_suc = array.array("d",suc)
          except TypeError:
            raise TypeError("Argument suc has wrong type") from None
          else:
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
        else:
          if memview_suc.ndim != 1:
            raise TypeError("Argument suc must be one-dimensional")
          if memview_suc.format != "d":
            _tmparray_suc = array.array("d",suc)
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
      copyback_slx = False
      if slx is None:
        slx_ = None
        memview_slx = None
      else:
        try:
          memview_slx = memoryview(slx)
        except TypeError:
          try:
            _tmparray_slx = array.array("d",slx)
          except TypeError:
            raise TypeError("Argument slx has wrong type") from None
          else:
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
        else:
          if memview_slx.ndim != 1:
            raise TypeError("Argument slx must be one-dimensional")
          if memview_slx.format != "d":
            _tmparray_slx = array.array("d",slx)
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
      copyback_sux = False
      if sux is None:
        sux_ = None
        memview_sux = None
      else:
        try:
          memview_sux = memoryview(sux)
        except TypeError:
          try:
            _tmparray_sux = array.array("d",sux)
          except TypeError:
            raise TypeError("Argument sux has wrong type") from None
          else:
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
        else:
          if memview_sux.ndim != 1:
            raise TypeError("Argument sux must be one-dimensional")
          if memview_sux.format != "d":
            _tmparray_sux = array.array("d",sux)
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
      copyback_snx = False
      if snx is None:
        snx_ = None
        memview_snx = None
      else:
        try:
          memview_snx = memoryview(snx)
        except TypeError:
          try:
            _tmparray_snx = array.array("d",snx)
          except TypeError:
            raise TypeError("Argument snx has wrong type") from None
          else:
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
        else:
          if memview_snx.ndim != 1:
            raise TypeError("Argument snx must be one-dimensional")
          if memview_snx.format != "d":
            _tmparray_snx = array.array("d",snx)
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
      _res_putsolution,_retargs_putsolution = self.__obj.putsolution_iOOOOOOOOOOO_13(whichsol,skc_,skx_,skn_,memview_xc,memview_xx,memview_y,memview_slc,memview_suc,memview_slx,memview_sux,memview_snx)
      if _res_putsolution != 0:
        _,_msg_putsolution = self.__getlasterror(_res_putsolution)
        raise Error(rescode(_res_putsolution),_msg_putsolution)
    def putsolution(self,*args,**kwds):
      """
      Inserts a solution.
    
      putsolution(whichsol,
                  skc,
                  skx,
                  skn,
                  xc,
                  xx,
                  y,
                  slc,
                  suc,
                  slx,
                  sux,
                  snx)
        [skc : array(mosek.stakey)]  Status keys for the constraints.  
        [skn : array(mosek.stakey)]  Status keys for the conic constraints.  
        [skx : array(mosek.stakey)]  Status keys for the variables.  
        [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
        [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
        [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
        [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
        [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [xc : array(float64)]  Primal constraint solution.  
        [xx : array(float64)]  Primal variable solution.  
        [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
      """
      return self.__putsolution_iOOOOOOOOOOO_13(*args,**kwds)
    def __putsolutionnew_iOOOOOOOOOOOO_14(self,whichsol,skc,skx,skn,xc,xx,y,slc,suc,slx,sux,snx,doty):
      if skc is None:
        skc_ = None
      else:
        # i
        _tmparray_skc_ = array.array("i",skc)
        skc_ = memoryview(_tmparray_skc_)
      if skx is None:
        skx_ = None
      else:
        # i
        _tmparray_skx_ = array.array("i",skx)
        skx_ = memoryview(_tmparray_skx_)
      if skn is None:
        skn_ = None
      else:
        # i
        _tmparray_skn_ = array.array("i",skn)
        skn_ = memoryview(_tmparray_skn_)
      copyback_xc = False
      if xc is None:
        xc_ = None
        memview_xc = None
      else:
        try:
          memview_xc = memoryview(xc)
        except TypeError:
          try:
            _tmparray_xc = array.array("d",xc)
          except TypeError:
            raise TypeError("Argument xc has wrong type") from None
          else:
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
        else:
          if memview_xc.ndim != 1:
            raise TypeError("Argument xc must be one-dimensional")
          if memview_xc.format != "d":
            _tmparray_xc = array.array("d",xc)
            memview_xc = memoryview(_tmparray_xc)
            copyback_xc = True
            xc_ = _tmparray_xc
      copyback_xx = False
      if xx is None:
        xx_ = None
        memview_xx = None
      else:
        try:
          memview_xx = memoryview(xx)
        except TypeError:
          try:
            _tmparray_xx = array.array("d",xx)
          except TypeError:
            raise TypeError("Argument xx has wrong type") from None
          else:
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
        else:
          if memview_xx.ndim != 1:
            raise TypeError("Argument xx must be one-dimensional")
          if memview_xx.format != "d":
            _tmparray_xx = array.array("d",xx)
            memview_xx = memoryview(_tmparray_xx)
            copyback_xx = True
            xx_ = _tmparray_xx
      copyback_y = False
      if y is None:
        y_ = None
        memview_y = None
      else:
        try:
          memview_y = memoryview(y)
        except TypeError:
          try:
            _tmparray_y = array.array("d",y)
          except TypeError:
            raise TypeError("Argument y has wrong type") from None
          else:
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
        else:
          if memview_y.ndim != 1:
            raise TypeError("Argument y must be one-dimensional")
          if memview_y.format != "d":
            _tmparray_y = array.array("d",y)
            memview_y = memoryview(_tmparray_y)
            copyback_y = True
            y_ = _tmparray_y
      copyback_slc = False
      if slc is None:
        slc_ = None
        memview_slc = None
      else:
        try:
          memview_slc = memoryview(slc)
        except TypeError:
          try:
            _tmparray_slc = array.array("d",slc)
          except TypeError:
            raise TypeError("Argument slc has wrong type") from None
          else:
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
        else:
          if memview_slc.ndim != 1:
            raise TypeError("Argument slc must be one-dimensional")
          if memview_slc.format != "d":
            _tmparray_slc = array.array("d",slc)
            memview_slc = memoryview(_tmparray_slc)
            copyback_slc = True
            slc_ = _tmparray_slc
      copyback_suc = False
      if suc is None:
        suc_ = None
        memview_suc = None
      else:
        try:
          memview_suc = memoryview(suc)
        except TypeError:
          try:
            _tmparray_suc = array.array("d",suc)
          except TypeError:
            raise TypeError("Argument suc has wrong type") from None
          else:
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
        else:
          if memview_suc.ndim != 1:
            raise TypeError("Argument suc must be one-dimensional")
          if memview_suc.format != "d":
            _tmparray_suc = array.array("d",suc)
            memview_suc = memoryview(_tmparray_suc)
            copyback_suc = True
            suc_ = _tmparray_suc
      copyback_slx = False
      if slx is None:
        slx_ = None
        memview_slx = None
      else:
        try:
          memview_slx = memoryview(slx)
        except TypeError:
          try:
            _tmparray_slx = array.array("d",slx)
          except TypeError:
            raise TypeError("Argument slx has wrong type") from None
          else:
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
        else:
          if memview_slx.ndim != 1:
            raise TypeError("Argument slx must be one-dimensional")
          if memview_slx.format != "d":
            _tmparray_slx = array.array("d",slx)
            memview_slx = memoryview(_tmparray_slx)
            copyback_slx = True
            slx_ = _tmparray_slx
      copyback_sux = False
      if sux is None:
        sux_ = None
        memview_sux = None
      else:
        try:
          memview_sux = memoryview(sux)
        except TypeError:
          try:
            _tmparray_sux = array.array("d",sux)
          except TypeError:
            raise TypeError("Argument sux has wrong type") from None
          else:
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
        else:
          if memview_sux.ndim != 1:
            raise TypeError("Argument sux must be one-dimensional")
          if memview_sux.format != "d":
            _tmparray_sux = array.array("d",sux)
            memview_sux = memoryview(_tmparray_sux)
            copyback_sux = True
            sux_ = _tmparray_sux
      copyback_snx = False
      if snx is None:
        snx_ = None
        memview_snx = None
      else:
        try:
          memview_snx = memoryview(snx)
        except TypeError:
          try:
            _tmparray_snx = array.array("d",snx)
          except TypeError:
            raise TypeError("Argument snx has wrong type") from None
          else:
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
        else:
          if memview_snx.ndim != 1:
            raise TypeError("Argument snx must be one-dimensional")
          if memview_snx.format != "d":
            _tmparray_snx = array.array("d",snx)
            memview_snx = memoryview(_tmparray_snx)
            copyback_snx = True
            snx_ = _tmparray_snx
      copyback_doty = False
      if doty is None:
        doty_ = None
        memview_doty = None
      else:
        try:
          memview_doty = memoryview(doty)
        except TypeError:
          try:
            _tmparray_doty = array.array("d",doty)
          except TypeError:
            raise TypeError("Argument doty has wrong type") from None
          else:
            memview_doty = memoryview(_tmparray_doty)
            copyback_doty = True
            doty_ = _tmparray_doty
        else:
          if memview_doty.ndim != 1:
            raise TypeError("Argument doty must be one-dimensional")
          if memview_doty.format != "d":
            _tmparray_doty = array.array("d",doty)
            memview_doty = memoryview(_tmparray_doty)
            copyback_doty = True
            doty_ = _tmparray_doty
      _res_putsolutionnew,_retargs_putsolutionnew = self.__obj.putsolutionnew_iOOOOOOOOOOOO_14(whichsol,skc_,skx_,skn_,memview_xc,memview_xx,memview_y,memview_slc,memview_suc,memview_slx,memview_sux,memview_snx,memview_doty)
      if _res_putsolutionnew != 0:
        _,_msg_putsolutionnew = self.__getlasterror(_res_putsolutionnew)
        raise Error(rescode(_res_putsolutionnew),_msg_putsolutionnew)
    def putsolutionnew(self,*args,**kwds):
      """
      Inserts a solution.
    
      putsolutionnew(whichsol,
                     skc,
                     skx,
                     skn,
                     xc,
                     xx,
                     y,
                     slc,
                     suc,
                     slx,
                     sux,
                     snx,
                     doty)
        [doty : array(float64)]  Dual variables corresponding to affine conic constraints.  
        [skc : array(mosek.stakey)]  Status keys for the constraints.  
        [skn : array(mosek.stakey)]  Status keys for the conic constraints.  
        [skx : array(mosek.stakey)]  Status keys for the variables.  
        [slc : array(float64)]  Dual variables corresponding to the lower bounds on the constraints.  
        [slx : array(float64)]  Dual variables corresponding to the lower bounds on the variables.  
        [snx : array(float64)]  Dual variables corresponding to the conic constraints on the variables.  
        [suc : array(float64)]  Dual variables corresponding to the upper bounds on the constraints.  
        [sux : array(float64)]  Dual variables corresponding to the upper bounds on the variables.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [xc : array(float64)]  Primal constraint solution.  
        [xx : array(float64)]  Primal variable solution.  
        [y : array(float64)]  Vector of dual variables corresponding to the constraints.  
      """
      return self.__putsolutionnew_iOOOOOOOOOOOO_14(*args,**kwds)
    def __putconsolutioni_iiiddd_7(self,i,whichsol,sk,x,sl,su):
      _res_putconsolutioni,_retargs_putconsolutioni = self.__obj.putconsolutioni_iiiddd_7(i,whichsol,sk,x,sl,su)
      if _res_putconsolutioni != 0:
        _,_msg_putconsolutioni = self.__getlasterror(_res_putconsolutioni)
        raise Error(rescode(_res_putconsolutioni),_msg_putconsolutioni)
    def putconsolutioni(self,*args,**kwds):
      """
      Sets the primal and dual solution information for a single constraint.
    
      putconsolutioni(i,whichsol,sk,x,sl,su)
        [i : int32]  Index of the constraint.  
        [sk : mosek.stakey]  Status key of the constraint.  
        [sl : float64]  Solution value of the dual variable associated with the lower bound.  
        [su : float64]  Solution value of the dual variable associated with the upper bound.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [x : float64]  Primal solution value of the constraint.  
      """
      return self.__putconsolutioni_iiiddd_7(*args,**kwds)
    def __putvarsolutionj_iiidddd_8(self,j,whichsol,sk,x,sl,su,sn):
      _res_putvarsolutionj,_retargs_putvarsolutionj = self.__obj.putvarsolutionj_iiidddd_8(j,whichsol,sk,x,sl,su,sn)
      if _res_putvarsolutionj != 0:
        _,_msg_putvarsolutionj = self.__getlasterror(_res_putvarsolutionj)
        raise Error(rescode(_res_putvarsolutionj),_msg_putvarsolutionj)
    def putvarsolutionj(self,*args,**kwds):
      """
      Sets the primal and dual solution information for a single variable.
    
      putvarsolutionj(j,whichsol,sk,x,sl,su,sn)
        [j : int32]  Index of the variable.  
        [sk : mosek.stakey]  Status key of the variable.  
        [sl : float64]  Solution value of the dual variable associated with the lower bound.  
        [sn : float64]  Solution value of the dual variable associated with the conic constraint.  
        [su : float64]  Solution value of the dual variable associated with the upper bound.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [x : float64]  Primal solution value of the variable.  
      """
      return self.__putvarsolutionj_iiidddd_8(*args,**kwds)
    def __putsolutionyi_iid_4(self,i,whichsol,y):
      _res_putsolutionyi,_retargs_putsolutionyi = self.__obj.putsolutionyi_iid_4(i,whichsol,y)
      if _res_putsolutionyi != 0:
        _,_msg_putsolutionyi = self.__getlasterror(_res_putsolutionyi)
        raise Error(rescode(_res_putsolutionyi),_msg_putsolutionyi)
    def putsolutionyi(self,*args,**kwds):
      """
      Inputs the dual variable of a solution.
    
      putsolutionyi(i,whichsol,y)
        [i : int32]  Index of the dual variable.  
        [whichsol : mosek.soltype]  Selects a solution.  
        [y : float64]  Solution value of the dual variable.  
      """
      return self.__putsolutionyi_iid_4(*args,**kwds)
    def __putstrparam_is_3(self,param,parvalue):
      _res_putstrparam,_retargs_putstrparam = self.__obj.putstrparam_is_3(param,parvalue)
      if _res_putstrparam != 0:
        _,_msg_putstrparam = self.__getlasterror(_res_putstrparam)
        raise Error(rescode(_res_putstrparam),_msg_putstrparam)
    def putstrparam(self,*args,**kwds):
      """
      Sets a string parameter.
    
      putstrparam(param,parvalue)
        [param : mosek.sparam]  Which parameter.  
        [parvalue : str]  Parameter value.  
      """
      return self.__putstrparam_is_3(*args,**kwds)
    def __puttaskname_s_2(self,taskname):
      _res_puttaskname,_retargs_puttaskname = self.__obj.puttaskname_s_2(taskname)
      if _res_puttaskname != 0:
        _,_msg_puttaskname = self.__getlasterror(_res_puttaskname)
        raise Error(rescode(_res_puttaskname),_msg_puttaskname)
    def puttaskname(self,*args,**kwds):
      """
      Assigns a new name to the task.
    
      puttaskname(taskname)
        [taskname : str]  Name assigned to the task.  
      """
      return self.__puttaskname_s_2(*args,**kwds)
    def __putvartype_ii_3(self,j,vartype):
      _res_putvartype,_retargs_putvartype = self.__obj.putvartype_ii_3(j,vartype)
      if _res_putvartype != 0:
        _,_msg_putvartype = self.__getlasterror(_res_putvartype)
        raise Error(rescode(_res_putvartype),_msg_putvartype)
    def putvartype(self,*args,**kwds):
      """
      Sets the variable type of one variable.
    
      putvartype(j,vartype)
        [j : int32]  Index of the variable.  
        [vartype : mosek.variabletype]  The new variable type.  
      """
      return self.__putvartype_ii_3(*args,**kwds)
    def __putvartypelist_OO_3(self,subj,vartype):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if vartype is None:
        vartype_ = None
      else:
        # i
        _tmparray_vartype_ = array.array("i",vartype)
        vartype_ = memoryview(_tmparray_vartype_)
      _res_putvartypelist,_retargs_putvartypelist = self.__obj.putvartypelist_OO_3(memview_subj,vartype_)
      if _res_putvartypelist != 0:
        _,_msg_putvartypelist = self.__getlasterror(_res_putvartypelist)
        raise Error(rescode(_res_putvartypelist),_msg_putvartypelist)
    def putvartypelist(self,*args,**kwds):
      """
      Sets the variable type for one or more variables.
    
      putvartypelist(subj,vartype)
        [subj : array(int32)]  A list of variable indexes for which the variable type should be changed.  
        [vartype : array(mosek.variabletype)]  A list of variable types.  
      """
      return self.__putvartypelist_OO_3(*args,**kwds)
    def __readdataformat_sii_4(self,filename,format,compress):
      _res_readdataformat,_retargs_readdataformat = self.__obj.readdataformat_sii_4(filename,format,compress)
      if _res_readdataformat != 0:
        _,_msg_readdataformat = self.__getlasterror(_res_readdataformat)
        raise Error(rescode(_res_readdataformat),_msg_readdataformat)
    def readdataformat(self,*args,**kwds):
      """
      Reads problem data from a file.
    
      readdataformat(filename,format,compress)
        [compress : mosek.compresstype]  File compression type.  
        [filename : str]  A valid file name.  
        [format : mosek.dataformat]  File data format.  
      """
      return self.__readdataformat_sii_4(*args,**kwds)
    def __readdataautoformat_s_2(self,filename):
      _res_readdataautoformat,_retargs_readdataautoformat = self.__obj.readdataautoformat_s_2(filename)
      if _res_readdataautoformat != 0:
        _,_msg_readdataautoformat = self.__getlasterror(_res_readdataautoformat)
        raise Error(rescode(_res_readdataautoformat),_msg_readdataautoformat)
    def readdata(self,*args,**kwds):
      """
      Reads problem data from a file.
    
      readdata(filename)
        [filename : str]  A valid file name.  
      """
      return self.__readdataautoformat_s_2(*args,**kwds)
    def __readparamfile_s_2(self,filename):
      _res_readparamfile,_retargs_readparamfile = self.__obj.readparamfile_s_2(filename)
      if _res_readparamfile != 0:
        _,_msg_readparamfile = self.__getlasterror(_res_readparamfile)
        raise Error(rescode(_res_readparamfile),_msg_readparamfile)
    def readparamfile(self,*args,**kwds):
      """
      Reads a parameter file.
    
      readparamfile(filename)
        [filename : str]  A valid file name.  
      """
      return self.__readparamfile_s_2(*args,**kwds)
    def __readsolution_is_3(self,whichsol,filename):
      _res_readsolution,_retargs_readsolution = self.__obj.readsolution_is_3(whichsol,filename)
      if _res_readsolution != 0:
        _,_msg_readsolution = self.__getlasterror(_res_readsolution)
        raise Error(rescode(_res_readsolution),_msg_readsolution)
    def readsolution(self,*args,**kwds):
      """
      Reads a solution from a file.
    
      readsolution(whichsol,filename)
        [filename : str]  A valid file name.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__readsolution_is_3(*args,**kwds)
    def __readjsonsol_s_2(self,filename):
      _res_readjsonsol,_retargs_readjsonsol = self.__obj.readjsonsol_s_2(filename)
      if _res_readjsonsol != 0:
        _,_msg_readjsonsol = self.__getlasterror(_res_readjsonsol)
        raise Error(rescode(_res_readjsonsol),_msg_readjsonsol)
    def readjsonsol(self,*args,**kwds):
      """
      Reads a solution from a JSOL file.
    
      readjsonsol(filename)
        [filename : str]  A valid file name.  
      """
      return self.__readjsonsol_s_2(*args,**kwds)
    def __readsummary_i_2(self,whichstream):
      _res_readsummary,_retargs_readsummary = self.__obj.readsummary_i_2(whichstream)
      if _res_readsummary != 0:
        _,_msg_readsummary = self.__getlasterror(_res_readsummary)
        raise Error(rescode(_res_readsummary),_msg_readsummary)
    def readsummary(self,*args,**kwds):
      """
      Prints information about last file read.
    
      readsummary(whichstream)
        [whichstream : mosek.streamtype]  Index of the stream.  
      """
      return self.__readsummary_i_2(*args,**kwds)
    def __resizetask_iiiLL_6(self,maxnumcon,maxnumvar,maxnumcone,maxnumanz,maxnumqnz):
      _res_resizetask,_retargs_resizetask = self.__obj.resizetask_iiiLL_6(maxnumcon,maxnumvar,maxnumcone,maxnumanz,maxnumqnz)
      if _res_resizetask != 0:
        _,_msg_resizetask = self.__getlasterror(_res_resizetask)
        raise Error(rescode(_res_resizetask),_msg_resizetask)
    def resizetask(self,*args,**kwds):
      """
      Resizes an optimization task.
    
      resizetask(maxnumcon,
                 maxnumvar,
                 maxnumcone,
                 maxnumanz,
                 maxnumqnz)
        [maxnumanz : int64]  New maximum number of linear non-zero elements.  
        [maxnumcon : int32]  New maximum number of constraints.  
        [maxnumcone : int32]  New maximum number of cones.  
        [maxnumqnz : int64]  New maximum number of quadratic non-zeros elements.  
        [maxnumvar : int32]  New maximum number of variables.  
      """
      return self.__resizetask_iiiLL_6(*args,**kwds)
    def __checkmemtask_si_3(self,file,line):
      _res_checkmemtask,_retargs_checkmemtask = self.__obj.checkmemtask_si_3(file,line)
      if _res_checkmemtask != 0:
        _,_msg_checkmemtask = self.__getlasterror(_res_checkmemtask)
        raise Error(rescode(_res_checkmemtask),_msg_checkmemtask)
    def checkmem(self,*args,**kwds):
      """
      Checks the memory allocated by the task.
    
      checkmem(file,line)
        [file : str]  File from which the function is called.  
        [line : int32]  Line in the file from which the function is called.  
      """
      return self.__checkmemtask_si_3(*args,**kwds)
    def __getmemusagetask__1(self):
      _res_getmemusagetask,_retargs_getmemusagetask = self.__obj.getmemusagetask__1()
      if _res_getmemusagetask != 0:
        _,_msg_getmemusagetask = self.__getlasterror(_res_getmemusagetask)
        raise Error(rescode(_res_getmemusagetask),_msg_getmemusagetask)
      else:
        (meminuse,maxmemuse) = _retargs_getmemusagetask
      return (meminuse,maxmemuse)
    def getmemusage(self,*args,**kwds):
      """
      Obtains information about the amount of memory used by a task.
    
      getmemusage() -> (meminuse,maxmemuse)
        [maxmemuse : int64]  Maximum amount of memory used by the task until now.  
        [meminuse : int64]  Amount of memory currently used by the task.  
      """
      return self.__getmemusagetask__1(*args,**kwds)
    def __setdefaults__1(self):
      _res_setdefaults,_retargs_setdefaults = self.__obj.setdefaults__1()
      if _res_setdefaults != 0:
        _,_msg_setdefaults = self.__getlasterror(_res_setdefaults)
        raise Error(rescode(_res_setdefaults),_msg_setdefaults)
    def setdefaults(self,*args,**kwds):
      """
      Resets all parameter values.
    
      setdefaults()
      """
      return self.__setdefaults__1(*args,**kwds)
    def __solutiondef_i_2(self,whichsol):
      _res_solutiondef,_retargs_solutiondef = self.__obj.solutiondef_i_2(whichsol)
      if _res_solutiondef != 0:
        _,_msg_solutiondef = self.__getlasterror(_res_solutiondef)
        raise Error(rescode(_res_solutiondef),_msg_solutiondef)
      else:
        (isdef) = _retargs_solutiondef
      return (isdef!=0)
    def solutiondef(self,*args,**kwds):
      """
      Checks whether a solution is defined.
    
      solutiondef(whichsol) -> (isdef)
        [isdef : bool]  Is non-zero if the requested solution is defined.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__solutiondef_i_2(*args,**kwds)
    def __deletesolution_i_2(self,whichsol):
      _res_deletesolution,_retargs_deletesolution = self.__obj.deletesolution_i_2(whichsol)
      if _res_deletesolution != 0:
        _,_msg_deletesolution = self.__getlasterror(_res_deletesolution)
        raise Error(rescode(_res_deletesolution),_msg_deletesolution)
    def deletesolution(self,*args,**kwds):
      """
      Undefine a solution and free the memory it uses.
    
      deletesolution(whichsol)
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__deletesolution_i_2(*args,**kwds)
    def __onesolutionsummary_ii_3(self,whichstream,whichsol):
      _res_onesolutionsummary,_retargs_onesolutionsummary = self.__obj.onesolutionsummary_ii_3(whichstream,whichsol)
      if _res_onesolutionsummary != 0:
        _,_msg_onesolutionsummary = self.__getlasterror(_res_onesolutionsummary)
        raise Error(rescode(_res_onesolutionsummary),_msg_onesolutionsummary)
    def onesolutionsummary(self,*args,**kwds):
      """
      Prints a short summary of a specified solution.
    
      onesolutionsummary(whichstream,whichsol)
        [whichsol : mosek.soltype]  Selects a solution.  
        [whichstream : mosek.streamtype]  Index of the stream.  
      """
      return self.__onesolutionsummary_ii_3(*args,**kwds)
    def __solutionsummary_i_2(self,whichstream):
      _res_solutionsummary,_retargs_solutionsummary = self.__obj.solutionsummary_i_2(whichstream)
      if _res_solutionsummary != 0:
        _,_msg_solutionsummary = self.__getlasterror(_res_solutionsummary)
        raise Error(rescode(_res_solutionsummary),_msg_solutionsummary)
    def solutionsummary(self,*args,**kwds):
      """
      Prints a short summary of the current solutions.
    
      solutionsummary(whichstream)
        [whichstream : mosek.streamtype]  Index of the stream.  
      """
      return self.__solutionsummary_i_2(*args,**kwds)
    def __updatesolutioninfo_i_2(self,whichsol):
      _res_updatesolutioninfo,_retargs_updatesolutioninfo = self.__obj.updatesolutioninfo_i_2(whichsol)
      if _res_updatesolutioninfo != 0:
        _,_msg_updatesolutioninfo = self.__getlasterror(_res_updatesolutioninfo)
        raise Error(rescode(_res_updatesolutioninfo),_msg_updatesolutioninfo)
    def updatesolutioninfo(self,*args,**kwds):
      """
      Update the information items related to the solution.
    
      updatesolutioninfo(whichsol)
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__updatesolutioninfo_i_2(*args,**kwds)
    def __optimizersummary_i_2(self,whichstream):
      _res_optimizersummary,_retargs_optimizersummary = self.__obj.optimizersummary_i_2(whichstream)
      if _res_optimizersummary != 0:
        _,_msg_optimizersummary = self.__getlasterror(_res_optimizersummary)
        raise Error(rescode(_res_optimizersummary),_msg_optimizersummary)
    def optimizersummary(self,*args,**kwds):
      """
      Prints a short summary with optimizer statistics from last optimization.
    
      optimizersummary(whichstream)
        [whichstream : mosek.streamtype]  Index of the stream.  
      """
      return self.__optimizersummary_i_2(*args,**kwds)
    def __strtoconetype_s_2(self,str):
      _res_strtoconetype,_retargs_strtoconetype = self.__obj.strtoconetype_s_2(str)
      if _res_strtoconetype != 0:
        _,_msg_strtoconetype = self.__getlasterror(_res_strtoconetype)
        raise Error(rescode(_res_strtoconetype),_msg_strtoconetype)
      else:
        (conetype) = _retargs_strtoconetype
      return (conetype(conetype))
    def strtoconetype(self,*args,**kwds):
      """
      Obtains a cone type code.
    
      strtoconetype(str) -> (conetype)
        [conetype : mosek.conetype]  The cone type corresponding to str.  
        [str : str]  String corresponding to the cone type code.  
      """
      return self.__strtoconetype_s_2(*args,**kwds)
    def __strtosk_s_2(self,str):
      _res_strtosk,_retargs_strtosk = self.__obj.strtosk_s_2(str)
      if _res_strtosk != 0:
        _,_msg_strtosk = self.__getlasterror(_res_strtosk)
        raise Error(rescode(_res_strtosk),_msg_strtosk)
      else:
        (sk) = _retargs_strtosk
      return (stakey(sk))
    def strtosk(self,*args,**kwds):
      """
      Obtains a status key.
    
      strtosk(str) -> (sk)
        [sk : mosek.stakey]  Status key corresponding to the string.  
        [str : str]  A status key abbreviation string.  
      """
      return self.__strtosk_s_2(*args,**kwds)
    def __writedata_s_2(self,filename):
      _res_writedata,_retargs_writedata = self.__obj.writedata_s_2(filename)
      if _res_writedata != 0:
        _,_msg_writedata = self.__getlasterror(_res_writedata)
        raise Error(rescode(_res_writedata),_msg_writedata)
    def writedata(self,*args,**kwds):
      """
      Writes problem data to a file.
    
      writedata(filename)
        [filename : str]  A valid file name.  
      """
      return self.__writedata_s_2(*args,**kwds)
    def __writetask_s_2(self,filename):
      _res_writetask,_retargs_writetask = self.__obj.writetask_s_2(filename)
      if _res_writetask != 0:
        _,_msg_writetask = self.__getlasterror(_res_writetask)
        raise Error(rescode(_res_writetask),_msg_writetask)
    def writetask(self,*args,**kwds):
      """
      Write a complete binary dump of the task data.
    
      writetask(filename)
        [filename : str]  A valid file name.  
      """
      return self.__writetask_s_2(*args,**kwds)
    def __writebsolution_si_3(self,filename,compress):
      _res_writebsolution,_retargs_writebsolution = self.__obj.writebsolution_si_3(filename,compress)
      if _res_writebsolution != 0:
        _,_msg_writebsolution = self.__getlasterror(_res_writebsolution)
        raise Error(rescode(_res_writebsolution),_msg_writebsolution)
    def writebsolution(self,*args,**kwds):
      """
      Write a binary dump of the task solution and information items.
    
      writebsolution(filename,compress)
        [compress : mosek.compresstype]  Data compression type.  
        [filename : str]  A valid file name.  
      """
      return self.__writebsolution_si_3(*args,**kwds)
    def __readbsolution_si_3(self,filename,compress):
      _res_readbsolution,_retargs_readbsolution = self.__obj.readbsolution_si_3(filename,compress)
      if _res_readbsolution != 0:
        _,_msg_readbsolution = self.__getlasterror(_res_readbsolution)
        raise Error(rescode(_res_readbsolution),_msg_readbsolution)
    def readbsolution(self,*args,**kwds):
      """
      Read a binary dump of the task solution and information items.
    
      readbsolution(filename,compress)
        [compress : mosek.compresstype]  Data compression type.  
        [filename : str]  A valid file name.  
      """
      return self.__readbsolution_si_3(*args,**kwds)
    def __writesolutionfile_s_2(self,filename):
      _res_writesolutionfile,_retargs_writesolutionfile = self.__obj.writesolutionfile_s_2(filename)
      if _res_writesolutionfile != 0:
        _,_msg_writesolutionfile = self.__getlasterror(_res_writesolutionfile)
        raise Error(rescode(_res_writesolutionfile),_msg_writesolutionfile)
    def writesolutionfile(self,*args,**kwds):
      """
      Write solution file in format determined by the filename
    
      writesolutionfile(filename)
        [filename : str]  A valid file name.  
      """
      return self.__writesolutionfile_s_2(*args,**kwds)
    def __readsolutionfile_s_2(self,filename):
      _res_readsolutionfile,_retargs_readsolutionfile = self.__obj.readsolutionfile_s_2(filename)
      if _res_readsolutionfile != 0:
        _,_msg_readsolutionfile = self.__getlasterror(_res_readsolutionfile)
        raise Error(rescode(_res_readsolutionfile),_msg_readsolutionfile)
    def readsolutionfile(self,*args,**kwds):
      """
      Read solution file in format determined by the filename
    
      readsolutionfile(filename)
        [filename : str]  A valid file name.  
      """
      return self.__readsolutionfile_s_2(*args,**kwds)
    def __readtask_s_2(self,filename):
      _res_readtask,_retargs_readtask = self.__obj.readtask_s_2(filename)
      if _res_readtask != 0:
        _,_msg_readtask = self.__getlasterror(_res_readtask)
        raise Error(rescode(_res_readtask),_msg_readtask)
    def readtask(self,*args,**kwds):
      """
      Load task data from a file.
    
      readtask(filename)
        [filename : str]  A valid file name.  
      """
      return self.__readtask_s_2(*args,**kwds)
    def __readopfstring_s_2(self,data):
      _res_readopfstring,_retargs_readopfstring = self.__obj.readopfstring_s_2(data)
      if _res_readopfstring != 0:
        _,_msg_readopfstring = self.__getlasterror(_res_readopfstring)
        raise Error(rescode(_res_readopfstring),_msg_readopfstring)
    def readopfstring(self,*args,**kwds):
      """
      Load task data from a string in OPF format.
    
      readopfstring(data)
        [data : str]  Problem data in text format.  
      """
      return self.__readopfstring_s_2(*args,**kwds)
    def __readlpstring_s_2(self,data):
      _res_readlpstring,_retargs_readlpstring = self.__obj.readlpstring_s_2(data)
      if _res_readlpstring != 0:
        _,_msg_readlpstring = self.__getlasterror(_res_readlpstring)
        raise Error(rescode(_res_readlpstring),_msg_readlpstring)
    def readlpstring(self,*args,**kwds):
      """
      Load task data from a string in LP format.
    
      readlpstring(data)
        [data : str]  Problem data in text format.  
      """
      return self.__readlpstring_s_2(*args,**kwds)
    def __readjsonstring_s_2(self,data):
      _res_readjsonstring,_retargs_readjsonstring = self.__obj.readjsonstring_s_2(data)
      if _res_readjsonstring != 0:
        _,_msg_readjsonstring = self.__getlasterror(_res_readjsonstring)
        raise Error(rescode(_res_readjsonstring),_msg_readjsonstring)
    def readjsonstring(self,*args,**kwds):
      """
      Load task data from a string in JSON format.
    
      readjsonstring(data)
        [data : str]  Problem data in text format.  
      """
      return self.__readjsonstring_s_2(*args,**kwds)
    def __readptfstring_s_2(self,data):
      _res_readptfstring,_retargs_readptfstring = self.__obj.readptfstring_s_2(data)
      if _res_readptfstring != 0:
        _,_msg_readptfstring = self.__getlasterror(_res_readptfstring)
        raise Error(rescode(_res_readptfstring),_msg_readptfstring)
    def readptfstring(self,*args,**kwds):
      """
      Load task data from a string in PTF format.
    
      readptfstring(data)
        [data : str]  Problem data in text format.  
      """
      return self.__readptfstring_s_2(*args,**kwds)
    def __writeparamfile_s_2(self,filename):
      _res_writeparamfile,_retargs_writeparamfile = self.__obj.writeparamfile_s_2(filename)
      if _res_writeparamfile != 0:
        _,_msg_writeparamfile = self.__getlasterror(_res_writeparamfile)
        raise Error(rescode(_res_writeparamfile),_msg_writeparamfile)
    def writeparamfile(self,*args,**kwds):
      """
      Writes all the parameters to a parameter file.
    
      writeparamfile(filename)
        [filename : str]  A valid file name.  
      """
      return self.__writeparamfile_s_2(*args,**kwds)
    def __getinfeasiblesubproblem_i_2(self,whichsol):
      _res_getinfeasiblesubproblem,_retargs_getinfeasiblesubproblem = self.__obj.getinfeasiblesubproblem_i_2(whichsol)
      if _res_getinfeasiblesubproblem != 0:
        _,_msg_getinfeasiblesubproblem = self.__getlasterror(_res_getinfeasiblesubproblem)
        raise Error(rescode(_res_getinfeasiblesubproblem),_msg_getinfeasiblesubproblem)
      else:
        (_inftask) = _retargs_getinfeasiblesubproblem
      return (Task(_inftask))
    def getinfeasiblesubproblem(self,*args,**kwds):
      """
      Obtains an infeasible subproblem.
    
      getinfeasiblesubproblem(whichsol) -> (inftask)
        [inftask : mosek.Task]  A new task containing the infeasible subproblem.  
        [whichsol : mosek.soltype]  Which solution to use when determining the infeasible subproblem.  
      """
      return self.__getinfeasiblesubproblem_i_2(*args,**kwds)
    def __writesolution_is_3(self,whichsol,filename):
      _res_writesolution,_retargs_writesolution = self.__obj.writesolution_is_3(whichsol,filename)
      if _res_writesolution != 0:
        _,_msg_writesolution = self.__getlasterror(_res_writesolution)
        raise Error(rescode(_res_writesolution),_msg_writesolution)
    def writesolution(self,*args,**kwds):
      """
      Write a solution to a file.
    
      writesolution(whichsol,filename)
        [filename : str]  A valid file name.  
        [whichsol : mosek.soltype]  Selects a solution.  
      """
      return self.__writesolution_is_3(*args,**kwds)
    def __writejsonsol_s_2(self,filename):
      _res_writejsonsol,_retargs_writejsonsol = self.__obj.writejsonsol_s_2(filename)
      if _res_writejsonsol != 0:
        _,_msg_writejsonsol = self.__getlasterror(_res_writejsonsol)
        raise Error(rescode(_res_writejsonsol),_msg_writejsonsol)
    def writejsonsol(self,*args,**kwds):
      """
      Writes a solution to a JSON file.
    
      writejsonsol(filename)
        [filename : str]  A valid file name.  
      """
      return self.__writejsonsol_s_2(*args,**kwds)
    def __primalsensitivity_OOOOOOOOOOOO_13(self,subi,marki,subj,markj,leftpricei,rightpricei,leftrangei,rightrangei,leftpricej,rightpricej,leftrangej,rightrangej):
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",subi)
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if marki is None:
        marki_ = None
      else:
        # i
        _tmparray_marki_ = array.array("i",marki)
        marki_ = memoryview(_tmparray_marki_)
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if markj is None:
        markj_ = None
      else:
        # i
        _tmparray_markj_ = array.array("i",markj)
        markj_ = memoryview(_tmparray_markj_)
      copyback_leftpricei = False
      if leftpricei is None:
        leftpricei_ = None
        memview_leftpricei = None
      else:
        try:
          memview_leftpricei = memoryview(leftpricei)
        except TypeError:
          try:
            _tmparray_leftpricei = array.array("d",[0 for _ in range(len(leftpricei))])
          except TypeError:
            raise TypeError("Argument leftpricei has wrong type") from None
          else:
            memview_leftpricei = memoryview(_tmparray_leftpricei)
            copyback_leftpricei = True
            leftpricei_ = _tmparray_leftpricei
        else:
          if memview_leftpricei.ndim != 1:
            raise TypeError("Argument leftpricei must be one-dimensional")
          if memview_leftpricei.format != "d":
            _tmparray_leftpricei = array.array("d",leftpricei)
            memview_leftpricei = memoryview(_tmparray_leftpricei)
            copyback_leftpricei = True
            leftpricei_ = _tmparray_leftpricei
      copyback_rightpricei = False
      if rightpricei is None:
        rightpricei_ = None
        memview_rightpricei = None
      else:
        try:
          memview_rightpricei = memoryview(rightpricei)
        except TypeError:
          try:
            _tmparray_rightpricei = array.array("d",[0 for _ in range(len(rightpricei))])
          except TypeError:
            raise TypeError("Argument rightpricei has wrong type") from None
          else:
            memview_rightpricei = memoryview(_tmparray_rightpricei)
            copyback_rightpricei = True
            rightpricei_ = _tmparray_rightpricei
        else:
          if memview_rightpricei.ndim != 1:
            raise TypeError("Argument rightpricei must be one-dimensional")
          if memview_rightpricei.format != "d":
            _tmparray_rightpricei = array.array("d",rightpricei)
            memview_rightpricei = memoryview(_tmparray_rightpricei)
            copyback_rightpricei = True
            rightpricei_ = _tmparray_rightpricei
      copyback_leftrangei = False
      if leftrangei is None:
        leftrangei_ = None
        memview_leftrangei = None
      else:
        try:
          memview_leftrangei = memoryview(leftrangei)
        except TypeError:
          try:
            _tmparray_leftrangei = array.array("d",[0 for _ in range(len(leftrangei))])
          except TypeError:
            raise TypeError("Argument leftrangei has wrong type") from None
          else:
            memview_leftrangei = memoryview(_tmparray_leftrangei)
            copyback_leftrangei = True
            leftrangei_ = _tmparray_leftrangei
        else:
          if memview_leftrangei.ndim != 1:
            raise TypeError("Argument leftrangei must be one-dimensional")
          if memview_leftrangei.format != "d":
            _tmparray_leftrangei = array.array("d",leftrangei)
            memview_leftrangei = memoryview(_tmparray_leftrangei)
            copyback_leftrangei = True
            leftrangei_ = _tmparray_leftrangei
      copyback_rightrangei = False
      if rightrangei is None:
        rightrangei_ = None
        memview_rightrangei = None
      else:
        try:
          memview_rightrangei = memoryview(rightrangei)
        except TypeError:
          try:
            _tmparray_rightrangei = array.array("d",[0 for _ in range(len(rightrangei))])
          except TypeError:
            raise TypeError("Argument rightrangei has wrong type") from None
          else:
            memview_rightrangei = memoryview(_tmparray_rightrangei)
            copyback_rightrangei = True
            rightrangei_ = _tmparray_rightrangei
        else:
          if memview_rightrangei.ndim != 1:
            raise TypeError("Argument rightrangei must be one-dimensional")
          if memview_rightrangei.format != "d":
            _tmparray_rightrangei = array.array("d",rightrangei)
            memview_rightrangei = memoryview(_tmparray_rightrangei)
            copyback_rightrangei = True
            rightrangei_ = _tmparray_rightrangei
      copyback_leftpricej = False
      if leftpricej is None:
        leftpricej_ = None
        memview_leftpricej = None
      else:
        try:
          memview_leftpricej = memoryview(leftpricej)
        except TypeError:
          try:
            _tmparray_leftpricej = array.array("d",[0 for _ in range(len(leftpricej))])
          except TypeError:
            raise TypeError("Argument leftpricej has wrong type") from None
          else:
            memview_leftpricej = memoryview(_tmparray_leftpricej)
            copyback_leftpricej = True
            leftpricej_ = _tmparray_leftpricej
        else:
          if memview_leftpricej.ndim != 1:
            raise TypeError("Argument leftpricej must be one-dimensional")
          if memview_leftpricej.format != "d":
            _tmparray_leftpricej = array.array("d",leftpricej)
            memview_leftpricej = memoryview(_tmparray_leftpricej)
            copyback_leftpricej = True
            leftpricej_ = _tmparray_leftpricej
      copyback_rightpricej = False
      if rightpricej is None:
        rightpricej_ = None
        memview_rightpricej = None
      else:
        try:
          memview_rightpricej = memoryview(rightpricej)
        except TypeError:
          try:
            _tmparray_rightpricej = array.array("d",[0 for _ in range(len(rightpricej))])
          except TypeError:
            raise TypeError("Argument rightpricej has wrong type") from None
          else:
            memview_rightpricej = memoryview(_tmparray_rightpricej)
            copyback_rightpricej = True
            rightpricej_ = _tmparray_rightpricej
        else:
          if memview_rightpricej.ndim != 1:
            raise TypeError("Argument rightpricej must be one-dimensional")
          if memview_rightpricej.format != "d":
            _tmparray_rightpricej = array.array("d",rightpricej)
            memview_rightpricej = memoryview(_tmparray_rightpricej)
            copyback_rightpricej = True
            rightpricej_ = _tmparray_rightpricej
      copyback_leftrangej = False
      if leftrangej is None:
        leftrangej_ = None
        memview_leftrangej = None
      else:
        try:
          memview_leftrangej = memoryview(leftrangej)
        except TypeError:
          try:
            _tmparray_leftrangej = array.array("d",[0 for _ in range(len(leftrangej))])
          except TypeError:
            raise TypeError("Argument leftrangej has wrong type") from None
          else:
            memview_leftrangej = memoryview(_tmparray_leftrangej)
            copyback_leftrangej = True
            leftrangej_ = _tmparray_leftrangej
        else:
          if memview_leftrangej.ndim != 1:
            raise TypeError("Argument leftrangej must be one-dimensional")
          if memview_leftrangej.format != "d":
            _tmparray_leftrangej = array.array("d",leftrangej)
            memview_leftrangej = memoryview(_tmparray_leftrangej)
            copyback_leftrangej = True
            leftrangej_ = _tmparray_leftrangej
      copyback_rightrangej = False
      if rightrangej is None:
        rightrangej_ = None
        memview_rightrangej = None
      else:
        try:
          memview_rightrangej = memoryview(rightrangej)
        except TypeError:
          try:
            _tmparray_rightrangej = array.array("d",[0 for _ in range(len(rightrangej))])
          except TypeError:
            raise TypeError("Argument rightrangej has wrong type") from None
          else:
            memview_rightrangej = memoryview(_tmparray_rightrangej)
            copyback_rightrangej = True
            rightrangej_ = _tmparray_rightrangej
        else:
          if memview_rightrangej.ndim != 1:
            raise TypeError("Argument rightrangej must be one-dimensional")
          if memview_rightrangej.format != "d":
            _tmparray_rightrangej = array.array("d",rightrangej)
            memview_rightrangej = memoryview(_tmparray_rightrangej)
            copyback_rightrangej = True
            rightrangej_ = _tmparray_rightrangej
      _res_primalsensitivity,_retargs_primalsensitivity = self.__obj.primalsensitivity_OOOOOOOOOOOO_13(memview_subi,marki_,memview_subj,markj_,memview_leftpricei,memview_rightpricei,memview_leftrangei,memview_rightrangei,memview_leftpricej,memview_rightpricej,memview_leftrangej,memview_rightrangej)
      if _res_primalsensitivity != 0:
        _,_msg_primalsensitivity = self.__getlasterror(_res_primalsensitivity)
        raise Error(rescode(_res_primalsensitivity),_msg_primalsensitivity)
      if copyback_leftpricei:
        for __tmp_1508 in range(len(leftpricei)): leftpricei[__tmp_1508] = leftpricei_[__tmp_1508]
      if copyback_rightpricei:
        for __tmp_1509 in range(len(rightpricei)): rightpricei[__tmp_1509] = rightpricei_[__tmp_1509]
      if copyback_leftrangei:
        for __tmp_1510 in range(len(leftrangei)): leftrangei[__tmp_1510] = leftrangei_[__tmp_1510]
      if copyback_rightrangei:
        for __tmp_1511 in range(len(rightrangei)): rightrangei[__tmp_1511] = rightrangei_[__tmp_1511]
      if copyback_leftpricej:
        for __tmp_1512 in range(len(leftpricej)): leftpricej[__tmp_1512] = leftpricej_[__tmp_1512]
      if copyback_rightpricej:
        for __tmp_1513 in range(len(rightpricej)): rightpricej[__tmp_1513] = rightpricej_[__tmp_1513]
      if copyback_leftrangej:
        for __tmp_1514 in range(len(leftrangej)): leftrangej[__tmp_1514] = leftrangej_[__tmp_1514]
      if copyback_rightrangej:
        for __tmp_1515 in range(len(rightrangej)): rightrangej[__tmp_1515] = rightrangej_[__tmp_1515]
    def __primalsensitivity_OOOOOOOOOOOO_5(self,subi,marki,subj,markj):
      if subi is None:
        raise TypeError("Argument subi may not be None")
      copyback_subi = False
      if subi is None:
        subi_ = None
        memview_subi = None
      else:
        try:
          memview_subi = memoryview(subi)
        except TypeError:
          try:
            _tmparray_subi = array.array("i",subi)
          except TypeError:
            raise TypeError("Argument subi has wrong type") from None
          else:
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
        else:
          if memview_subi.ndim != 1:
            raise TypeError("Argument subi must be one-dimensional")
          if memview_subi.format != "i":
            _tmparray_subi = array.array("i",subi)
            memview_subi = memoryview(_tmparray_subi)
            copyback_subi = True
            subi_ = _tmparray_subi
      if marki is None:
        marki_ = None
      else:
        # i
        _tmparray_marki_ = array.array("i",marki)
        marki_ = memoryview(_tmparray_marki_)
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      if markj is None:
        markj_ = None
      else:
        # i
        _tmparray_markj_ = array.array("i",markj)
        markj_ = memoryview(_tmparray_markj_)
      leftpricei_ = bytearray(0)
      rightpricei_ = bytearray(0)
      leftrangei_ = bytearray(0)
      rightrangei_ = bytearray(0)
      leftpricej_ = bytearray(0)
      rightpricej_ = bytearray(0)
      leftrangej_ = bytearray(0)
      rightrangej_ = bytearray(0)
      _res_primalsensitivity,_retargs_primalsensitivity = self.__obj.primalsensitivity_OOOOOOOOOOOO_5(memview_subi,marki_,memview_subj,markj_,leftpricei_,rightpricei_,leftrangei_,rightrangei_,leftpricej_,rightpricej_,leftrangej_,rightrangej_)
      if _res_primalsensitivity != 0:
        _,_msg_primalsensitivity = self.__getlasterror(_res_primalsensitivity)
        raise Error(rescode(_res_primalsensitivity),_msg_primalsensitivity)
      leftpricei = array.array("d")
      leftpricei.frombytes(leftpricei_)
      rightpricei = array.array("d")
      rightpricei.frombytes(rightpricei_)
      leftrangei = array.array("d")
      leftrangei.frombytes(leftrangei_)
      rightrangei = array.array("d")
      rightrangei.frombytes(rightrangei_)
      leftpricej = array.array("d")
      leftpricej.frombytes(leftpricej_)
      rightpricej = array.array("d")
      rightpricej.frombytes(rightpricej_)
      leftrangej = array.array("d")
      leftrangej.frombytes(leftrangej_)
      rightrangej = array.array("d")
      rightrangej.frombytes(rightrangej_)
      return (leftpricei,rightpricei,leftrangei,rightrangei,leftpricej,rightpricej,leftrangej,rightrangej)
    def primalsensitivity(self,*args,**kwds):
      """
      Perform sensitivity analysis on bounds.
    
      primalsensitivity(subi,
                        marki,
                        subj,
                        markj,
                        leftpricei,
                        rightpricei,
                        leftrangei,
                        rightrangei,
                        leftpricej,
                        rightpricej,
                        leftrangej,
                        rightrangej)
      primalsensitivity(subi,marki,subj,markj) -> 
                       (leftpricei,
                        rightpricei,
                        leftrangei,
                        rightrangei,
                        leftpricej,
                        rightpricej,
                        leftrangej,
                        rightrangej)
        [leftpricei : array(float64)]  Left shadow price for constraints.  
        [leftpricej : array(float64)]  Left shadow price for variables.  
        [leftrangei : array(float64)]  Left range for constraints.  
        [leftrangej : array(float64)]  Left range for variables.  
        [marki : array(mosek.mark)]  Mark which constraint bounds to analyze.  
        [markj : array(mosek.mark)]  Mark which variable bounds to analyze.  
        [rightpricei : array(float64)]  Right shadow price for constraints.  
        [rightpricej : array(float64)]  Right shadow price for variables.  
        [rightrangei : array(float64)]  Right range for constraints.  
        [rightrangej : array(float64)]  Right range for variables.  
        [subi : array(int32)]  Indexes of constraints to analyze.  
        [subj : array(int32)]  Indexes of variables to analyze.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 13: return self.__primalsensitivity_OOOOOOOOOOOO_13(*args,**kwds)
      elif len(args)+len(kwds)+1 == 5: return self.__primalsensitivity_OOOOOOOOOOOO_5(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __sensitivityreport_i_2(self,whichstream):
      _res_sensitivityreport,_retargs_sensitivityreport = self.__obj.sensitivityreport_i_2(whichstream)
      if _res_sensitivityreport != 0:
        _,_msg_sensitivityreport = self.__getlasterror(_res_sensitivityreport)
        raise Error(rescode(_res_sensitivityreport),_msg_sensitivityreport)
    def sensitivityreport(self,*args,**kwds):
      """
      Creates a sensitivity report.
    
      sensitivityreport(whichstream)
        [whichstream : mosek.streamtype]  Index of the stream.  
      """
      return self.__sensitivityreport_i_2(*args,**kwds)
    def __dualsensitivity_OOOOO_6(self,subj,leftpricej,rightpricej,leftrangej,rightrangej):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      copyback_leftpricej = False
      if leftpricej is None:
        leftpricej_ = None
        memview_leftpricej = None
      else:
        try:
          memview_leftpricej = memoryview(leftpricej)
        except TypeError:
          try:
            _tmparray_leftpricej = array.array("d",[0 for _ in range(len(leftpricej))])
          except TypeError:
            raise TypeError("Argument leftpricej has wrong type") from None
          else:
            memview_leftpricej = memoryview(_tmparray_leftpricej)
            copyback_leftpricej = True
            leftpricej_ = _tmparray_leftpricej
        else:
          if memview_leftpricej.ndim != 1:
            raise TypeError("Argument leftpricej must be one-dimensional")
          if memview_leftpricej.format != "d":
            _tmparray_leftpricej = array.array("d",leftpricej)
            memview_leftpricej = memoryview(_tmparray_leftpricej)
            copyback_leftpricej = True
            leftpricej_ = _tmparray_leftpricej
      copyback_rightpricej = False
      if rightpricej is None:
        rightpricej_ = None
        memview_rightpricej = None
      else:
        try:
          memview_rightpricej = memoryview(rightpricej)
        except TypeError:
          try:
            _tmparray_rightpricej = array.array("d",[0 for _ in range(len(rightpricej))])
          except TypeError:
            raise TypeError("Argument rightpricej has wrong type") from None
          else:
            memview_rightpricej = memoryview(_tmparray_rightpricej)
            copyback_rightpricej = True
            rightpricej_ = _tmparray_rightpricej
        else:
          if memview_rightpricej.ndim != 1:
            raise TypeError("Argument rightpricej must be one-dimensional")
          if memview_rightpricej.format != "d":
            _tmparray_rightpricej = array.array("d",rightpricej)
            memview_rightpricej = memoryview(_tmparray_rightpricej)
            copyback_rightpricej = True
            rightpricej_ = _tmparray_rightpricej
      copyback_leftrangej = False
      if leftrangej is None:
        leftrangej_ = None
        memview_leftrangej = None
      else:
        try:
          memview_leftrangej = memoryview(leftrangej)
        except TypeError:
          try:
            _tmparray_leftrangej = array.array("d",[0 for _ in range(len(leftrangej))])
          except TypeError:
            raise TypeError("Argument leftrangej has wrong type") from None
          else:
            memview_leftrangej = memoryview(_tmparray_leftrangej)
            copyback_leftrangej = True
            leftrangej_ = _tmparray_leftrangej
        else:
          if memview_leftrangej.ndim != 1:
            raise TypeError("Argument leftrangej must be one-dimensional")
          if memview_leftrangej.format != "d":
            _tmparray_leftrangej = array.array("d",leftrangej)
            memview_leftrangej = memoryview(_tmparray_leftrangej)
            copyback_leftrangej = True
            leftrangej_ = _tmparray_leftrangej
      copyback_rightrangej = False
      if rightrangej is None:
        rightrangej_ = None
        memview_rightrangej = None
      else:
        try:
          memview_rightrangej = memoryview(rightrangej)
        except TypeError:
          try:
            _tmparray_rightrangej = array.array("d",[0 for _ in range(len(rightrangej))])
          except TypeError:
            raise TypeError("Argument rightrangej has wrong type") from None
          else:
            memview_rightrangej = memoryview(_tmparray_rightrangej)
            copyback_rightrangej = True
            rightrangej_ = _tmparray_rightrangej
        else:
          if memview_rightrangej.ndim != 1:
            raise TypeError("Argument rightrangej must be one-dimensional")
          if memview_rightrangej.format != "d":
            _tmparray_rightrangej = array.array("d",rightrangej)
            memview_rightrangej = memoryview(_tmparray_rightrangej)
            copyback_rightrangej = True
            rightrangej_ = _tmparray_rightrangej
      _res_dualsensitivity,_retargs_dualsensitivity = self.__obj.dualsensitivity_OOOOO_6(memview_subj,memview_leftpricej,memview_rightpricej,memview_leftrangej,memview_rightrangej)
      if _res_dualsensitivity != 0:
        _,_msg_dualsensitivity = self.__getlasterror(_res_dualsensitivity)
        raise Error(rescode(_res_dualsensitivity),_msg_dualsensitivity)
      if copyback_leftpricej:
        for __tmp_1529 in range(len(leftpricej)): leftpricej[__tmp_1529] = leftpricej_[__tmp_1529]
      if copyback_rightpricej:
        for __tmp_1530 in range(len(rightpricej)): rightpricej[__tmp_1530] = rightpricej_[__tmp_1530]
      if copyback_leftrangej:
        for __tmp_1531 in range(len(leftrangej)): leftrangej[__tmp_1531] = leftrangej_[__tmp_1531]
      if copyback_rightrangej:
        for __tmp_1532 in range(len(rightrangej)): rightrangej[__tmp_1532] = rightrangej_[__tmp_1532]
    def __dualsensitivity_OOOOO_2(self,subj):
      if subj is None:
        raise TypeError("Argument subj may not be None")
      copyback_subj = False
      if subj is None:
        subj_ = None
        memview_subj = None
      else:
        try:
          memview_subj = memoryview(subj)
        except TypeError:
          try:
            _tmparray_subj = array.array("i",subj)
          except TypeError:
            raise TypeError("Argument subj has wrong type") from None
          else:
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
        else:
          if memview_subj.ndim != 1:
            raise TypeError("Argument subj must be one-dimensional")
          if memview_subj.format != "i":
            _tmparray_subj = array.array("i",subj)
            memview_subj = memoryview(_tmparray_subj)
            copyback_subj = True
            subj_ = _tmparray_subj
      leftpricej_ = bytearray(0)
      rightpricej_ = bytearray(0)
      leftrangej_ = bytearray(0)
      rightrangej_ = bytearray(0)
      _res_dualsensitivity,_retargs_dualsensitivity = self.__obj.dualsensitivity_OOOOO_2(memview_subj,leftpricej_,rightpricej_,leftrangej_,rightrangej_)
      if _res_dualsensitivity != 0:
        _,_msg_dualsensitivity = self.__getlasterror(_res_dualsensitivity)
        raise Error(rescode(_res_dualsensitivity),_msg_dualsensitivity)
      leftpricej = array.array("d")
      leftpricej.frombytes(leftpricej_)
      rightpricej = array.array("d")
      rightpricej.frombytes(rightpricej_)
      leftrangej = array.array("d")
      leftrangej.frombytes(leftrangej_)
      rightrangej = array.array("d")
      rightrangej.frombytes(rightrangej_)
      return (leftpricej,rightpricej,leftrangej,rightrangej)
    def dualsensitivity(self,*args,**kwds):
      """
      Performs sensitivity analysis on objective coefficients.
    
      dualsensitivity(subj,
                      leftpricej,
                      rightpricej,
                      leftrangej,
                      rightrangej)
      dualsensitivity(subj) -> 
                     (leftpricej,
                      rightpricej,
                      leftrangej,
                      rightrangej)
        [leftpricej : array(float64)]  Left shadow prices for requested coefficients.  
        [leftrangej : array(float64)]  Left range for requested coefficients.  
        [rightpricej : array(float64)]  Right shadow prices for requested coefficients.  
        [rightrangej : array(float64)]  Right range for requested coefficients.  
        [subj : array(int32)]  Indexes of objective coefficients to analyze.  
      """
      if False: pass
      elif len(args)+len(kwds)+1 == 6: return self.__dualsensitivity_OOOOO_6(*args,**kwds)
      elif len(args)+len(kwds)+1 == 2: return self.__dualsensitivity_OOOOO_2(*args,**kwds)
      else: raise TypeError("Missing positional arguments")
    def __optimizermt_ss_3(self,address,accesstoken):
      _res_optimizermt,_retargs_optimizermt = self.__obj.optimizermt_ss_3(address,accesstoken)
      if _res_optimizermt != 0:
        _,_msg_optimizermt = self.__getlasterror(_res_optimizermt)
        raise Error(rescode(_res_optimizermt),_msg_optimizermt)
      else:
        (trmcode) = _retargs_optimizermt
      return (rescode(trmcode))
    def optimizermt(self,*args,**kwds):
      """
      Offload the optimization task to a solver server and wait for the solution.
    
      optimizermt(address,accesstoken) -> (trmcode)
        [accesstoken : str]  Access token.  
        [address : str]  Address of the OptServer.  
        [trmcode : mosek.rescode]  Is either OK or a termination response code.  
      """
      return self.__optimizermt_ss_3(*args,**kwds)
    def __asyncoptimize_ssO_3(self,address,accesstoken):
      token = bytearray(0)
      _res_asyncoptimize,_retargs_asyncoptimize = self.__obj.asyncoptimize_ssO_3(address,accesstoken,token)
      if _res_asyncoptimize != 0:
        _,_msg_asyncoptimize = self.__getlasterror(_res_asyncoptimize)
        raise Error(rescode(_res_asyncoptimize),_msg_asyncoptimize)
      __tmp_1538 = token.find(b"\0")
      if __tmp_1538 >= 0:
        token = token[:__tmp_1538]
      return (token.decode("utf-8",errors="ignore"))
    def asyncoptimize(self,*args,**kwds):
      """
      Offload the optimization task to a solver server in asynchronous mode.
    
      asyncoptimize(address,accesstoken) -> (token)
        [accesstoken : str]  Access token.  
        [address : str]  Address of the OptServer.  
        [token : str]  Returns the task token.  
      """
      return self.__asyncoptimize_ssO_3(*args,**kwds)
    def __asyncstop_sss_4(self,address,accesstoken,token):
      _res_asyncstop,_retargs_asyncstop = self.__obj.asyncstop_sss_4(address,accesstoken,token)
      if _res_asyncstop != 0:
        _,_msg_asyncstop = self.__getlasterror(_res_asyncstop)
        raise Error(rescode(_res_asyncstop),_msg_asyncstop)
    def asyncstop(self,*args,**kwds):
      """
      Request that the job identified by the token is terminated.
    
      asyncstop(address,accesstoken,token)
        [accesstoken : str]  Access token.  
        [address : str]  Address of the OptServer.  
        [token : str]  The task token.  
      """
      return self.__asyncstop_sss_4(*args,**kwds)
    def __asyncpoll_sss_4(self,address,accesstoken,token):
      _res_asyncpoll,_retargs_asyncpoll = self.__obj.asyncpoll_sss_4(address,accesstoken,token)
      if _res_asyncpoll != 0:
        _,_msg_asyncpoll = self.__getlasterror(_res_asyncpoll)
        raise Error(rescode(_res_asyncpoll),_msg_asyncpoll)
      else:
        (respavailable,resp,trm) = _retargs_asyncpoll
      return (respavailable!=0,rescode(resp),rescode(trm))
    def asyncpoll(self,*args,**kwds):
      """
      Requests information about the status of the remote job.
    
      asyncpoll(address,accesstoken,token) -> (respavailable,resp,trm)
        [accesstoken : str]  Access token.  
        [address : str]  Address of the OptServer.  
        [resp : mosek.rescode]  Is the response code from the remote solver.  
        [respavailable : bool]  Indicates if a remote response is available.  
        [token : str]  The task token.  
        [trm : mosek.rescode]  Is either OK or a termination response code.  
      """
      return self.__asyncpoll_sss_4(*args,**kwds)
    def __asyncgetresult_sss_4(self,address,accesstoken,token):
      _res_asyncgetresult,_retargs_asyncgetresult = self.__obj.asyncgetresult_sss_4(address,accesstoken,token)
      if _res_asyncgetresult != 0:
        _,_msg_asyncgetresult = self.__getlasterror(_res_asyncgetresult)
        raise Error(rescode(_res_asyncgetresult),_msg_asyncgetresult)
      else:
        (respavailable,resp,trm) = _retargs_asyncgetresult
      return (respavailable!=0,rescode(resp),rescode(trm))
    def asyncgetresult(self,*args,**kwds):
      """
      Request a solution from a remote job.
    
      asyncgetresult(address,accesstoken,token) -> (respavailable,resp,trm)
        [accesstoken : str]  Access token.  
        [address : str]  Address of the OptServer.  
        [resp : mosek.rescode]  Is the response code from the remote solver.  
        [respavailable : bool]  Indicates if a remote response is available.  
        [token : str]  The task token.  
        [trm : mosek.rescode]  Is either OK or a termination response code.  
      """
      return self.__asyncgetresult_sss_4(*args,**kwds)
    def __putoptserverhost_s_2(self,host):
      _res_putoptserverhost,_retargs_putoptserverhost = self.__obj.putoptserverhost_s_2(host)
      if _res_putoptserverhost != 0:
        _,_msg_putoptserverhost = self.__getlasterror(_res_putoptserverhost)
        raise Error(rescode(_res_putoptserverhost),_msg_putoptserverhost)
    def putoptserverhost(self,*args,**kwds):
      """
      Specify an OptServer for remote calls.
    
      putoptserverhost(host)
        [host : str]  A URL specifying the optimization server to be used.  
      """
      return self.__putoptserverhost_s_2(*args,**kwds)



class LinAlg:
  __env = Env()

  axpy = __env.axpy
  dot  = __env.dot
  gemv = __env.gemv
  gemm = __env.gemm
  syrk = __env.syrk
  syeig = __env.syeig
  syevd = __env.syevd
  potrf = __env.potrf
