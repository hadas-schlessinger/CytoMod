import axios from "axios";


export async function setParameters(projectName, comperament, luminex, logCytokines, k, outcomes, covariates, logColumns, cytokines) {
    const data = new FormData()
    data.append('name_data', projectName['projectName'])
    data.append('name_compartment', comperament)
    data.append('luminex', luminex)    
    data.append('log_transform', logCytokines)
    data.append('max_testing_k', k)
    data.append('outcomes', outcomes)
    data.append('covariates', covariates)
    data.append('log_column_names', logColumns)
    data.append('cytokines', cytokines)
    console.log({data: data});
    // let source = axios.CancelToken.source()
    // setTimeout(() => {
    //     source.cancel();
    // }, 10*60*60*10000);
    // let timeout = setTimeout(() => source.cancel('Timeout'), 10*60*60*10000); // connection timeout here in ms 
    // clearTimeout(timeout); 
    axios.defaults.timeout = 10*60*60*10000;
    const set_response = await axios.post("/generate", data)
    .then(response => {axios.post("/clustering", response.data)
    .then(response => {
        console.log({response: response});
        const absolute =  axios.post("/absolute", response.data)
        const adjusted = axios.post("/adjusted", response.data)
        axios.all([absolute, adjusted]).then(axios.spread((...responses) => {
         return responses}))
                 
    

})
})
}
