import axios from "axios";


export async function setParameters(comperament, luminex, logCytokines, k, outcomes, covariates, logColumns, cytokines) {
    const data = new FormData()
    data.append('name_compartment', comperament)
    data.append('luminex', luminex)    
    data.append('og_transform', logCytokines)
    data.append('max_testing_k', k)
    data.append('outcomes', outcomes)
    data.append('covariates', covariates)
    data.append('log_column_names', logColumns)
    data.append('cytokines', cytokines)
    const response = await axios.post("/generate",data)      
    return response.data 
}