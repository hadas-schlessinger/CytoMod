import React from 'react'

export default function PreperTable(modules){
    const table = []
    modules.map((module, index)=>
                table.push({Module: index+1 , Cytokines : module.substring(1).replace("[", "").replace("]", "").replace("'", "").replace("'", "")})    
    )
    console.log(table)
    return(
        table
    )
 
  
} 
 