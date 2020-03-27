import React from 'react'
import NevigationAbsAdj from './NevigationAbsAdj'
import beckgroungTransperant from '../../beckgroungTransperant.png'


export default function ModelsClusteringPanel() {
    return (
        <div style={{backgroundImage: `url(${beckgroungTransperant})`}}>
            <NevigationAbsAdj / >
           <h1>Models Clustering</h1>
        </div>
    )
}
