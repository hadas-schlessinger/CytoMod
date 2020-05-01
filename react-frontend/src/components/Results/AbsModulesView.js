import React from 'react'
import { Table } from 'semantic-ui-react'


export default function AbsModulesView(props) {
    const exportTableToExcel = (tableID, filename = '') =>{
        var downloadLink;
        var dataType = 'application/vnd.ms-excel';
        var tableSelect = document.getElementById(tableID);
        var tableHTML = tableSelect.outerHTML.replace(/ /g, '%20');
    
        // Specify file name
        filename = filename?filename+'.xls':'excel_data.xls';
    
        // Create download link element
        downloadLink = document.createElement("a");
    
        document.body.appendChild(downloadLink);
    
        if(navigator.msSaveOrOpenBlob){
            var blob = new Blob(['\ufeff', tableHTML], {
                type: dataType
            });
            navigator.msSaveOrOpenBlob( blob, filename);
        }else{
            // Create a link to the file
            downloadLink.href = 'data:' + dataType + ', ' + tableHTML;
    
            // Setting the file name
            downloadLink.download = filename;
    
            //triggering the function
            downloadLink.click();
        }
    }
    if(props.results.absolute[props.row]!=null){
        const ModelStr = props.results.absolute[props.row]
        const AbsModules = ModelStr.substring(0,ModelStr.length-2).split("]")
        console.log(AbsModules)
        return (
            
            <React.Fragment>
            <h3>Absolute Module</h3>
            {/* <table id="tblDataAdj">
            <tbody> */}
                <Table color={'teal'} key={'teal'}>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Module</Table.HeaderCell>
                    <Table.HeaderCell>Cytokines</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
           { AbsModules.map((module, index)=>
                <Table.Body>
                  <Table.Row>
                     <Table.Cell>{index+1} </Table.Cell>
                        <Table.Cell>{module.substring(1).replace("[", "").replace("]", "").replace("'", "").replace("'", "")} </Table.Cell>
                    
                  </Table.Row>
                      {/* {{module}.map(cytokine=>
                            <p>{cytokine}</p>
                                            )} */}
                 
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


                