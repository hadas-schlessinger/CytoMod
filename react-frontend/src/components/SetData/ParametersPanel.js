import React from 'react'
import beckgroungTransperant from '../../beckgroungTransperant.png'
import ParametersForm from './ParametersForm'

export default function ParametersPanel() {
    return (
        <div style={{backgroundImage: `url(${beckgroungTransperant})`}}>
            <ParametersForm / >
        </div>
    )
}
