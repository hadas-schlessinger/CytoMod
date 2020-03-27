import React from 'react'
import NevigationAbsAdj from './NevigationAbsAdj'
import beckgroungTransperant from '../../beckgroungTransperant.png'

export default function ModelsCorrelationPanel() {
    return (
        <div style={{backgroundImage: `url(${beckgroungTransperant})`}}>
            <NevigationAbsAdj / >
            <h1>Models Correlation</h1>
        </div>
    )
}
