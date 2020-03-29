import React from 'react'
import transperantBackground from '../../transperantBackground.png'
import ParametersForm from './ParametersForm'

export default function ParametersPanel() {
    return (
        <div style={{backgroundImage: `url(${transperantBackground})`}}>
            <ParametersForm / >
        </div>
    )
}
