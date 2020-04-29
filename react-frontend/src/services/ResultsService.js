import axios from "axios";

export async function getResults(name, id) {
    const data = new FormData()
    console.log({name: name})
    data.append('name_data', name)
    data.append('id', id)
    console.log({data: data});
    return await axios.post("/results", data)      
}

