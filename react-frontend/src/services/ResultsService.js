import axios from "axios";

export async function getResults(id) {
    const data = new FormData()
    data.append('id', id)
    console.log({data: data});
    return await axios.post("/results", data)      
}

