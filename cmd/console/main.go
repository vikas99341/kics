package main

import (
	"github.com/Checkmarx/kics/internal/console"
	"github.com/pkg/profile"
)

func main() { // nolint:funlen,gocyclo
	defer profile.Start(profile.CPUProfile, profile.ProfilePath(".")).Stop()
	if err := console.Execute(); err != nil {
		// os.Exit(1)
	}
}
