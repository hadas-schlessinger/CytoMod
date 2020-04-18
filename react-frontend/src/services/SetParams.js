import axios from "axios";


export async function setParameters(projectName, comperament, luminex, logCytokines, k, outcomes, covariates, logColumns, cytokines) {
    const data = new FormData()
    data.append('name_data', projectName['projectName'])
    data.append('name_compartment', comperament)
    data.append('luminex', luminex)    
    data.append('log_transform', logCytokines)
    data.append('max_testing_k', k)
    data.append('outcomes', outcomes)
    console.log(outcomes)
    data.append('covariates', covariates)
    data.append('log_column_names', logColumns)
    data.append('cytokines', cytokines)
    console.log({data: data});
    return await axios.post("/generate", data)
    
    
    
        }

    export async function methodStatus(projectName, formID) {
        const data = new FormData()
        data.append('name_data', projectName)
        data.append('id', formID)
        console.log({data: data});
       return await axios.post("/status", data)

      
        // let source = axios.CancelToken.source()
        // setTimeout(() => {
        //     source.cancel();
        // }, 10*60*60*10000);
        // let timeout = setTimeout(() => source.cancel('Timeout'), 10*60*60*10000); // connection timeout here in ms 
        // clearTimeout(timeout); 
        // axios.defaults.timeout = 10*60*60*10000;
    
        
            }
                 
    

