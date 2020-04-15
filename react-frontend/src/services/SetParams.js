import axios from "axios";


export async function setParameters(projectName, comperament, luminex, logCytokines, k, outcomes, covariates, logColumns, cytokines) {
    const data = new FormData()
    data.append('name_data', projectName['projectName'])
    data.append('name_compartment', comperament)
    data.append('luminex', luminex)    
    data.append('log_transform', logCytokines)
    console.log({logCytokines: logCytokines});
    data.append('max_testing_k', k)
    data.append('outcomes', outcomes)
    data.append('covariates', covariates)
    data.append('log_column_names', logColumns)
    data.append('cytokines', cytokines)
    console.log({data: data});
    // const source = axios.CancelToken.source();
    // let timeout = setTimeout(() => source.cancel('Timeout'), 10*60*60*10000);
    
// axios.get('http://localhost:3000',)
//     .then(() => { clearTimeout(timeout); console.log('hello there') });
    // const source = axios.CancelToken.source()
    // setTimeout(() => {
    //       source.cancel()
    //   }, 10*60*60*10000) // connection timeout here in ms
    axios.defaults.timeout = 10*60*60*10000;
    // { timeout: 10*60*60*10000, cancelToken: source.token }
    const response = await axios.post("/generate", data, ) 
    console.log({response: response});
    return response
}