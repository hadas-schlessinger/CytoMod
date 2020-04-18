import React from 'react'
import Set from './Set'
import LoadingState from'./LoadingState'


export default function LoadingPage() {
    return (
        <div>
           <h3 style = {{textAlign: 'center'}}>please wait while the server calculates the method</h3> 
           <LoadingState />
        </div>
    )
}
