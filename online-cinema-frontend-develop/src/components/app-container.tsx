import React, { createContext, useContext, useState } from 'react'

interface GlobalContextType {
  searchVisible: boolean
  setSearchResult: (visible: boolean) => void
}

const GlobalContext = createContext<GlobalContextType>({
  searchVisible: false,
  setSearchResult: () => {},
})

export const useGlobalContext = () => useContext(GlobalContext)

export const AppContainer = ({ children }: { children: React.ReactNode }) => {
  const [searchVisible, setSearchVisible] = useState(false)

  const value = {
    searchVisible,
    setSearchResult: setSearchVisible,
  }

  return (
    <GlobalContext.Provider value={value}>
      <div className="min-h-screen bg-body text-white">{children}</div>
    </GlobalContext.Provider>
  )
}
