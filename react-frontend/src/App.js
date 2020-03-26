import React , { useEffect } from 'react';
import './App.css';
import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { NavigationBar } from './components/NavigationBar';
import { Home } from './components/Home/Home';
import SetData from './components/SetData/SetData';

function App() {
  // useEffect(() => {
  //   fetch('/').then(response => {
  //     response.json().then("Hi");
  //   })
  //   return () => {
  //   }
  // }, [input])
  return (
    <div >
    <React.Fragment>
      <Router>
      <NavigationBar />
        <Switch>
          <Route exact path="/" component={Home} />
          <Route exact path="/set" component={SetData} />
          {/* <Route component={NoMatch} /> */}
        </Switch>
      </Router>
    </React.Fragment>
    </div>
  );
}

export default App;
