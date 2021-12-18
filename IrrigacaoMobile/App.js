import * as React from 'react';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { NavigationContainer } from '@react-navigation/native';

import HomeScreen from './HomeScreen';
import IrrigacaoScreen from './IrrigacaoScreen';

const Drawer = createDrawerNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Drawer.Navigator initialRouteName="Home">
        <Drawer.Screen name="Home" component={HomeScreen} />
        <Drawer.Screen name="Irrigar" component={IrrigacaoScreen} />
      </Drawer.Navigator>
    </NavigationContainer>
  );
}