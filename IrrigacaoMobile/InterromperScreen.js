import * as React from 'react';
import { Button, View, ToastAndroid } from 'react-native';
import RNPickerSelect from 'react-native-picker-select';
var data = require("./Data")

class InterromperScreen extends React.Component {

    constructor(props) {
      super(props);
      this.state = {
        valve:0
      }
    }

  getItems(){
    if (data.configData == undefined){
      return []
    }
    valves = data.configData.valves
    items = []
    for (i = 0; i < valves.length; i++){
      item = {label:valves[i].name, value:i}
      items.push(item)
    }
    return items;
  }


  interrupt(){
    
      var navigation = this.props.navigation;

      timer = hour+":"+minute+":00";
      fetch('http://'+data.IP+':8080/irrigate/'+this.state.valve+'/'+timer,{
            method:"PUT"
        })
        .then(res => res.text())
        .then(resText => JSON.parse(resText.replace(/'/g, '"')))
        .then(resJson => {
            if (resJson.status == true){
              ToastAndroid.show("Irrigação iniciada", ToastAndroid.SHORT);
              navigation.navigate("Home");
            } else {
              ToastAndroid.show("Falha ao iniciar irrigação", ToastAndroid.SHORT);
            }
        }).catch(e => console.log(e));

    
  }

  render(){
    items = this.getItems()

    return (
      <View style={{ flex: 1, alignItems: 'center'}}>

        <RNPickerSelect
            onValueChange={(value) => {this.setState({valve:value})} }
            items={items}
        />

        <Button onPress={this.interrupt.bind(this)} title="Interromper"></Button>

      </View>
    );
  }
}

export default IrrigacaoScreen;