import React from 'react'

export default function LoadingPage() {
    return (
        <div>
           <h3 style = {{textAlign: 'center'}}>please wait while the server calculates the method</h3> 
           <React.Fragment>
            <div className='loader'></div>
            <div style={{ textAlign: "center" }}>Calculating...</div>
            </React.Fragment>
        </div>
    )
}
