# -*- coding: utf-8 -*-
"""
Created on Wed May  2 14:37:14 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import pyautogui,time

pl_names=[
'Primus Telecommunications Group, Incorporated',
'Citadel Broadcasting Corporation',
'Motor Coach Industries International, Inc.',
'Beazer Homes USA, Inc.',
'True Temper Sports, Inc.',
'Visteon Corporation',
'CMP Susquehanna Corp',
'BI-LO, LLC (Old)',
'Pliant Corporation (Old)',
'Buffets, Inc. (Old)',
'Smurfit-Stone Container Enterprises (Old)',
'Workflow Management, Inc.',
'Spectrum Brands, Inc.',
'Source Interlink Companies Inc.',
'Atrium Corporation',
'Chemtura Corporation',
'Journal Register Company',
'Newark Group, Inc. (The)',
'Euramax International, Inc.',
'Fleetwood Enterprises Inc.',
'NextMedia Operating, Inc. (Old)',
'Portola Packaging, Inc.',
'Nexstar Broadcasting, Inc.',
'VeraSun Energy Corporation',
'NV Broadcasting, LLC',
'American Achievement Corporation',
'PRC, LLC',
'United Subcontractors Inc.',
'Pacific Lumber Co.',
'Pac-West Telecomm, Inc.',
'Coinmach Service Corp.',
'BearingPoint, Inc.',
'Express Energy Services Operating, LP',
'Hines Horticulture, Inc.',
'SuperMedia Inc.',
'Penton Business Media Holdings, Inc.',
'Emmis Communications Corporation',
'Foamex L.P.',
'iHeartCommunications, Inc.',
'Duane Reade, Inc.',
'Masonite Corporation',
'Six Flags Inc. (Old)',
'Six Flags Inc. (Old)',
'Port Townsend Paper Corporation',
'RBS Global, Inc.',
'Lazy Days R.V. Center, Inc.',
'Axiall Corporation',
'Tribune Media Company',
'Caesars Entertainment Corporation',
'MagnaChip Semiconductor Corporation',
'Young Broadcasting Inc.',
'Appvion, Inc.',
'Recycled Paper Greetings, Inc.',
'Caraustar Industries, Inc.',
'Wellman, Inc.',
'Haights Cross Communications, Inc.',
'Big West Oil, LLC (Old)',
'Aventine Renewable Energy Holdings (Old)',
'ION Media Networks, Inc.',
'Mark IV Industries, Inc. (Reorganized)',
'Key Plastics LLC',
'American Media Operations, Inc.',
'Plastech Engineered Products, Inc.',
'Vertis, Inc. (Old)',
'Suncom Wireless, Inc',
'RathGibson, Inc.',
'Pilgrims Pride Corporation (Old)',
'Citation Corporation',
'Metaldyne Corporation',
'JHT Holdings, Inc.',
'Merisant Worldwide, Inc.',
'Kimball Hill, Inc.',
'Finlay Fine Jewelry Corporation',
'Finlay Fine Jewelry Corporation',
'U.S. Shipping Partners LP',
'Noranda Aluminum Holding Corporation',
'OSI Restaurant Partners, LLC',
'Realogy Group LLC',
'Pierre Foods, Inc. (Old)',
'Headwaters Incorporated',
'Dayton Superior Corporation',
'YRC Worldwide Inc.',
'Regent Broadcasting LLC',
'Hawaiian Telcom Communications, Inc.',
'Electrical Components Intl. Inc. (Old)',
'Lenox Group, Inc.',
'Alion Science and Technology Corp',
'Propex Inc.',
'Movie Gallery, Inc.',
'Movie Gallery, Inc.',
'Builders FirstSource, Inc.',
'NTK Holdings, Inc.',
'Ford Motor Company',
'Jacuzzi Brands Corp.',
'Linens N Things, Inc.',
'Rhodes Companies, LLC (The)',
'Aleris International Inc.',
'Spheris Inc.',
'Momentive Performance Materials Inc. (Old)',
'Simmons Company',
'Quality Home Brands Holdings LLC (OLD)',
'Cygnus Business Media, Inc.',
'Charter Communications Inc.',
'FairPoint Communications, Inc.',
'Lyondell Chemical Company',
'Libbey Glass Inc.',
'Milacron Inc.',
'Chesapeake Corporation',
'Black Gaming, LLC',
'TLC Vision Corporation',
'Freescale Semiconductor, Inc.',
'Sensata Technologies B.V.',
'Affinity Group Holding, Inc.',
'Bally Total Fitness Holding Corporation',
'Bally Total Fitness Holding Corporation',
'Accuride Corporation (Old)',
'U.S. Concrete, Inc.',
'Chem Rx Corporation',
'Uno Restaurant Holdings Corporation',
'EnviroSolutions Holdings, Inc.',
'InSight Health Services Corp.',
'Constar International, Inc.',
'Legends Gaming, LLC (OLD)',
'Neff Corp.',
'Neff Corp.',
'Spansion, LLC',
'Penn Traffic Company',
'Wornick Company (The)',
'Century Aluminum Company',
'Neenah Foundry Company',
'Frontier Airlines, Inc.',
'Quantum Corporation',
'Champion Enterprises, Inc.',
'Readers Digest Association, Inc. ',
'Lear Corporation',
'Stallion Oilfield Holdings, Inc.',
'Cooper-Standard Automotive Inc.',
'Xerium Technologies, Inc.',
'R.H. Donnelley Inc. (Old)']

#%%


time.sleep(10)
for name in pl_names:
    
	pyautogui.moveTo(398, 172)
	pyautogui.click(398, 172)
	pyautogui.typewrite(name)
	pyautogui.press('enter')	

	time.sleep(4)
	pyautogui.click(627, 416)
	time.sleep(3)	

	pyautogui.moveTo(533, 279)
	pyautogui.dragTo(601, 279, button='left')
	pyautogui.hotkey('ctrl', 'c')	
	
	pyautogui.hotkey('alt', 'tab')
	pyautogui.hotkey('ctrl', 'v')
	pyautogui.press('enter')
	pyautogui.hotkey('alt', 'tab')


#%%

pyautogui.position()
asdasd
