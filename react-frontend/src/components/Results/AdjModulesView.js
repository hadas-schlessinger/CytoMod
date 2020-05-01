import React from 'react'
import { Table } from 'semantic-ui-react'


export default function AbsModulesView(props) {
    
    if(props.results.adjusted[props.row]!=null){
        const ModelStr = props.results.adjusted[props.row]
        const AdjModules = ModelStr.substring(0,ModelStr.length-2).split("]")
        return (
            
            <React.Fragment>
            <h3>Adjusted Module</h3>
            {/* <table id="tblDataAdj">
            <tbody> */}
                <Table color={'teal'} key={'teal'}>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Module</Table.HeaderCell>
                    <Table.HeaderCell>Cytokines</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
           { AdjModules.map((module, index)=>
                <Table.Body>
                  <Table.Row>
                     <Table.Cell>{index+1} </Table.Cell>
                        <Table.Cell>{module.substring(1).replace("[", "").replace("]", "").replace("'", "").replace("'", "")} </Table.Cell>
                    
                  </Table.Row>
                 
                </Table.Body>
            
           
                                   )
            } 
                          </Table>
          
                </React.Fragment>
        )
    }
    return(
        <p></p>
    )
}


                